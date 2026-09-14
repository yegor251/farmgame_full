from pathlib import Path

from app.auth.telegram_init_data import TelegramAuthResult, TelegramInitDataValidator
from app.domain.transfer_info import Deposit, Withdraw
from app.persistence.contracts import UserRecord
from app.persistence.snapshot_store import SnapshotStore
from app.ws import protocol
from app.ws.connection_handler import ConnectionHandler


class _FakeWebSocket:
    async def close(self) -> None:
        pass


class _FakeUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, UserRecord] = {}
        self.created: list[tuple[int, int]] = []

    def seed(self, user_id: int, ref_id: int, active: bool) -> None:
        self._users[user_id] = UserRecord(user_id=user_id, ref_id=ref_id, active=active)

    async def player_by_id(self, user_id: int) -> UserRecord | None:
        return self._users.get(user_id)

    async def activate_user_by_id(self, user_id: int) -> bool:
        if user_id in self._users:
            self._users[user_id].active = True
        return True

    async def create_user(self, user_id: int, ref_id: int) -> bool:
        if user_id in self._users:
            return False
        self.created.append((user_id, ref_id))
        self._users[user_id] = UserRecord(user_id=user_id, ref_id=ref_id, active=False)
        return True


class _FakeDepositRepository:
    async def get_deposits_by_user_id(self, tg_id: int) -> list[Deposit]:
        return []

    async def close_deposit_by_transaction_id(self, transaction_id: int) -> bool:
        return True

    async def insert_deposit(self, deposit: Deposit) -> bool:
        return True


class _FakeWithdrawRepository:
    async def check_withdraw_by_info(self, transaction_id: int) -> Withdraw | None:
        return None

    async def register_withdraw(self, withdraw: Withdraw) -> bool:
        return True

    async def list_pending_withdraws(self, limit: int) -> list[Withdraw]:
        return []

    async def mark_withdraw_sent(self, transaction_id: int) -> bool:
        return True


def _handler(snapshot_dir: Path, user_repository: _FakeUserRepository) -> ConnectionHandler:
    return ConnectionHandler(
        websocket=_FakeWebSocket(),  # type: ignore[arg-type]
        init_data_validator=TelegramInitDataValidator("dummy-token"),
        snapshot_store=SnapshotStore(snapshot_dir),
        user_repository=user_repository,  # type: ignore[arg-type]
        deposit_repository=_FakeDepositRepository(),  # type: ignore[arg-type]
        withdraw_repository=_FakeWithdrawRepository(),  # type: ignore[arg-type]
    )


async def test_handle_connect_returns_none_when_auth_is_missing(tmp_path: Path) -> None:
    handler = _handler(tmp_path, _FakeUserRepository())

    game = await handler._handle_connect(protocol.Connect(auth=None))

    assert game is None


async def test_handle_connect_registers_new_verified_telegram_user(tmp_path: Path) -> None:
    users = _FakeUserRepository()
    handler = _handler(tmp_path, users)
    auth = TelegramAuthResult(tg_id=42, is_verified=True, ref_id=0)

    game = await handler._handle_connect(protocol.Connect(auth=auth))

    assert game is not None
    assert game.client_info.tg_id == 42
    assert users.created == [(42, 0)]


async def test_handle_connect_rejects_unknown_dev_fallback_user(tmp_path: Path) -> None:
    users = _FakeUserRepository()
    handler = _handler(tmp_path, users)
    auth = TelegramAuthResult(tg_id=2357501, is_verified=False, ref_id=0)

    game = await handler._handle_connect(protocol.Connect(auth=auth))

    assert game is None
    assert users.created == []


async def test_handle_connect_loads_existing_dev_fallback_user(tmp_path: Path) -> None:
    users = _FakeUserRepository()
    users.seed(2357501, ref_id=0, active=False)
    handler = _handler(tmp_path, users)
    auth = TelegramAuthResult(tg_id=2357501, is_verified=False, ref_id=0)

    game = await handler._handle_connect(protocol.Connect(auth=auth))

    assert game is not None
    assert game.client_info.tg_id == 2357501
    assert users.created == []


async def test_handle_connect_credits_referrer_wallet_on_registration(tmp_path: Path) -> None:
    users = _FakeUserRepository()
    handler = _handler(tmp_path, users)

    referrer_game = await handler._handle_connect(
        protocol.Connect(auth=TelegramAuthResult(tg_id=1, is_verified=True, ref_id=0))
    )
    assert referrer_game is not None

    referred_game = await handler._handle_connect(
        protocol.Connect(auth=TelegramAuthResult(tg_id=2, is_verified=True, ref_id=1))
    )
    assert referred_game is not None

    referrer_reloaded = handler._snapshot_store.load_game(1)
    assert referrer_reloaded.player.wallet.token_balance == 1000
    assert referrer_reloaded.client_info.referrals == [2]
