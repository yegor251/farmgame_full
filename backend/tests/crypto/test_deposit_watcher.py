from pathlib import Path

from app.crypto.deposit_cursor import DepositCursorStore
from app.crypto.deposit_watcher import DepositWatcher
from app.crypto.ton_api_models import (
    AccountEvent,
    EventAction,
    JettonInfo,
    JettonTransferAction,
    TonApiAddress,
    TonTransferAction,
)
from app.domain.transfer_info import Deposit

ACCOUNT_ID = "0:acc"
USDT_ADDRESS = "0:usdt"
TFC_ADDRESS = "0:tfc"


class _FakeEventsSource:
    def __init__(self, events: list[AccountEvent]) -> None:
        self._events = events
        self.requested_start_dates: list[int] = []

    async def get_account_events(
        self, account_id: str, limit: int, start_date: int
    ) -> list[AccountEvent]:
        self.requested_start_dates.append(start_date)
        return self._events


class _FakeDepositRepository:
    def __init__(self) -> None:
        self.inserted: list[Deposit] = []

    async def get_deposits_by_user_id(self, tg_id: int) -> list[Deposit]:
        raise NotImplementedError

    async def close_deposit_by_transaction_id(self, transaction_id: int) -> bool:
        raise NotImplementedError

    async def insert_deposit(self, deposit: Deposit) -> bool:
        self.inserted.append(deposit)
        return True


def _ton_transfer_event(event_id: str, timestamp: int, amount: int, comment: str) -> AccountEvent:
    return AccountEvent(
        event_id=event_id,
        timestamp=timestamp,
        actions=[
            EventAction(
                TonTransfer=TonTransferAction(
                    recipient=TonApiAddress(address=ACCOUNT_ID), amount=amount, comment=comment
                )
            )
        ],
    )


def _jetton_transfer_event(
    event_id: str, timestamp: int, amount: int, jetton_address: str, comment: str = ""
) -> AccountEvent:
    return AccountEvent(
        event_id=event_id,
        timestamp=timestamp,
        actions=[
            EventAction(
                JettonTransfer=JettonTransferAction(
                    recipient=TonApiAddress(address=ACCOUNT_ID),
                    amount=amount,
                    jetton=JettonInfo(address=jetton_address),
                    comment=comment,
                )
            )
        ],
    )


def _make_watcher(
    events: list[AccountEvent], cursor_path: Path
) -> tuple[DepositWatcher, _FakeDepositRepository]:
    repository = _FakeDepositRepository()
    watcher = DepositWatcher(
        ton_client=_FakeEventsSource(events),
        deposit_repository=repository,
        cursor_store=DepositCursorStore(cursor_path),
        account_id=ACCOUNT_ID,
        usdt_jetton_address=USDT_ADDRESS,
        tfc_jetton_address=TFC_ADDRESS,
        events_limit=100,
        poll_interval_seconds=10,
    )
    return watcher, repository


async def test_poll_once_inserts_ton_transfer_with_parsed_tg_id(tmp_path: Path) -> None:
    events = [_ton_transfer_event("1", 100, 5_000_000, "42")]
    watcher, repository = _make_watcher(events, tmp_path / "cursor.txt")

    await watcher.poll_once()

    assert len(repository.inserted) == 1
    deposit = repository.inserted[0]
    assert deposit.tg_id == 42
    assert deposit.amount == 5_000_000
    assert deposit.jetton_signature == "TON"
    assert deposit.commentary == "donation"


async def test_poll_once_maps_jetton_addresses_to_signatures(tmp_path: Path) -> None:
    events = [
        _jetton_transfer_event("1", 100, 100, USDT_ADDRESS),
        _jetton_transfer_event("2", 101, 200, TFC_ADDRESS),
        _jetton_transfer_event("3", 102, 300, "0:unknown"),
    ]
    watcher, repository = _make_watcher(events, tmp_path / "cursor.txt")

    await watcher.poll_once()

    signatures = {d.transaction_id: d.jetton_signature for d in repository.inserted}
    assert signatures == {1: "USD", 2: "TFC"}


async def test_poll_once_defaults_tg_id_to_minus_one_for_non_numeric_comment(tmp_path: Path) -> None:
    events = [_ton_transfer_event("1", 100, 100, "")]
    watcher, repository = _make_watcher(events, tmp_path / "cursor.txt")

    await watcher.poll_once()

    assert repository.inserted[0].tg_id == -1


async def test_poll_once_stops_at_already_processed_transaction(tmp_path: Path) -> None:
    cursor_path = tmp_path / "cursor.txt"
    cursor_path.write_text("100\n2")
    events = [
        _ton_transfer_event("3", 200, 100, "1"),
        _ton_transfer_event("2", 150, 100, "1"),
        _ton_transfer_event("1", 100, 100, "1"),
    ]
    watcher, repository = _make_watcher(events, cursor_path)

    await watcher.poll_once()

    assert [d.transaction_id for d in repository.inserted] == [3]


async def test_poll_once_advances_and_persists_cursor(tmp_path: Path) -> None:
    cursor_path = tmp_path / "cursor.txt"
    events = [_ton_transfer_event("5", 500, 100, "1")]
    watcher, _ = _make_watcher(events, cursor_path)

    await watcher.poll_once()

    saved = DepositCursorStore(cursor_path).load()
    assert saved.last_transaction_id == 5
    assert saved.last_transaction_time == 500 - 1 - 1
