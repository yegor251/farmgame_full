from app.domain.game import Game
from app.domain.transfer_info import Deposit
from app.errors import GameErrorCode
from app.services import deposit_service


class _FakeDepositRepository:
    def __init__(self, deposits: list[Deposit], close_succeeds: bool = True) -> None:
        self._deposits = deposits
        self._close_succeeds = close_succeeds
        self.closed_transaction_ids: list[int] = []

    async def get_deposits_by_user_id(self, tg_id: int) -> list[Deposit]:
        return self._deposits

    async def close_deposit_by_transaction_id(self, transaction_id: int) -> bool:
        self.closed_transaction_ids.append(transaction_id)
        return self._close_succeeds


def _deposit(jetton_signature: str, amount: int = 100) -> Deposit:
    return Deposit(
        transaction_id=1,
        active=True,
        tg_id=1,
        amount=amount,
        time_stamp=0,
        jetton_signature=jetton_signature,
        commentary="",
    )


def test_proceed_to_balance_credits_matching_wallet_field() -> None:
    game = Game(tg_id=1, ref_id=0)

    deposit_service.proceed_to_balance(game.player, 100, "TON")
    deposit_service.proceed_to_balance(game.player, 200, "USD")
    deposit_service.proceed_to_balance(game.player, 300, "TFC")

    assert game.player.wallet.ton_balance == 100
    assert game.player.wallet.usdt_balance == 200
    assert game.player.wallet.token_balance == 300


def test_proceed_to_balance_ignores_unknown_signature() -> None:
    game = Game(tg_id=1, ref_id=0)

    deposit_service.proceed_to_balance(game.player, 100, "UNKNOWN")

    assert game.player.wallet.ton_balance == 0
    assert game.player.wallet.usdt_balance == 0
    assert game.player.wallet.token_balance == 0


def test_claim_rejects_out_of_range_index() -> None:
    game = Game(tg_id=1, ref_id=0)

    assert deposit_service.claim(game, 0) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_claim_rejects_already_claimed_deposit() -> None:
    game = Game(tg_id=1, ref_id=0)
    deposit = _deposit("TON")
    deposit.active = False
    game.transfer_info.deposits.append(deposit)

    assert deposit_service.claim(game, 0) == GameErrorCode.DEPOSIT_ALREADY_ACTIVATED


def test_claim_credits_wallet_and_deactivates_deposit_on_success() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.transfer_info.deposits.append(_deposit("TON", amount=500))

    result = deposit_service.claim(game, 0)

    assert result == GameErrorCode.OK
    assert game.player.wallet.ton_balance == 500
    assert game.transfer_info.deposits[0].active is False


async def test_check_appends_deposits_closed_successfully() -> None:
    game = Game(tg_id=1, ref_id=0)
    repository = _FakeDepositRepository([_deposit("TON")])

    result = await deposit_service.check(game, repository)

    assert result == GameErrorCode.OK
    assert len(game.transfer_info.deposits) == 1
    assert repository.closed_transaction_ids == [1]


async def test_check_reports_payment_error_when_close_fails() -> None:
    game = Game(tg_id=1, ref_id=0)
    repository = _FakeDepositRepository([_deposit("TON")], close_succeeds=False)

    result = await deposit_service.check(game, repository)

    assert result == GameErrorCode.PAYMENT_ERROR
    assert game.transfer_info.deposits == []
