from app.domain.game import Game
from app.domain.transfer_info import Withdraw
from app.errors import GameErrorCode
from app.services import withdraw_service


class _FakeWithdrawRepository:
    def __init__(
        self, status_by_transaction_id: dict[int, int] | None = None, register_succeeds: bool = True
    ) -> None:
        self._status_by_transaction_id = status_by_transaction_id or {}
        self._register_succeeds = register_succeeds
        self.registered: list[Withdraw] = []

    async def check_withdraw_by_info(self, transaction_id: int) -> Withdraw | None:
        status = self._status_by_transaction_id.get(transaction_id)
        if status is None:
            return None
        return Withdraw(
            transaction_id=transaction_id, status=status, tg_id=1, wallet="EQwallet", amount=0, time_stamp=0
        )

    async def register_withdraw(self, withdraw: Withdraw) -> bool:
        self.registered.append(withdraw)
        return self._register_succeeds


async def test_create_withdraw_rejects_when_not_enough_token_balance() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.wallet.token_balance = 0

    result = await withdraw_service.create_withdraw(game, 100, "EQwallet", _FakeWithdrawRepository())

    assert result == GameErrorCode.NOT_ENOUGH_MONEY


async def test_create_withdraw_rejects_when_not_enough_ton_for_fee() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.wallet.token_balance = 1000
    game.player.wallet.ton_balance = 0

    result = await withdraw_service.create_withdraw(game, 100, "EQwallet", _FakeWithdrawRepository())

    assert result == GameErrorCode.NOT_ENOUGH_MONEY


async def test_create_withdraw_reports_payment_error_when_registration_fails() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.wallet.token_balance = 1000
    game.player.wallet.ton_balance = 100_000_000

    result = await withdraw_service.create_withdraw(
        game, 100, "EQwallet", _FakeWithdrawRepository(register_succeeds=False)
    )

    assert result == GameErrorCode.PAYMENT_ERROR
    assert game.transfer_info.withdraws == []


async def test_create_withdraw_charges_balances_and_records_withdraw_on_success() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.wallet.token_balance = 1000
    game.player.wallet.ton_balance = 100_000_000

    result = await withdraw_service.create_withdraw(game, 100, "EQwallet", _FakeWithdrawRepository())

    assert result == GameErrorCode.OK
    assert game.player.wallet.token_balance == 900
    assert game.player.wallet.ton_balance == 0
    assert len(game.transfer_info.withdraws) == 1
    assert game.transfer_info.withdraws[0].wallet == "EQwallet"


async def test_get_current_status_defaults_to_zero_when_missing() -> None:
    status = await withdraw_service.get_current_status(1, _FakeWithdrawRepository())

    assert status == 0


async def test_get_current_status_returns_repository_status() -> None:
    status = await withdraw_service.get_current_status(1, _FakeWithdrawRepository({1: 2}))

    assert status == 2


async def test_check_all_withdraws_updates_status_for_every_tracked_withdraw() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.transfer_info.withdraws.append(
        Withdraw(transaction_id=1, status=0, tg_id=1, wallet="EQwallet", amount=100, time_stamp=0)
    )

    result = await withdraw_service.check_all_withdraws(game, _FakeWithdrawRepository({1: 3}))

    assert result == GameErrorCode.OK
    assert game.transfer_info.withdraws[0].status == 3
