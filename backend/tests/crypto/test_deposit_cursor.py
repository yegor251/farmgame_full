from pathlib import Path

from app.crypto.deposit_cursor import DepositCursorState, DepositCursorStore


def test_load_returns_zero_state_when_file_missing(tmp_path: Path) -> None:
    store = DepositCursorStore(tmp_path / "missing.txt")

    state = store.load()

    assert state.last_transaction_time == 0
    assert state.last_transaction_id == 0


def test_save_then_load_round_trips_state(tmp_path: Path) -> None:
    store = DepositCursorStore(tmp_path / "cursor.txt")

    store.save(DepositCursorState(last_transaction_time=1000, last_transaction_id=42))
    state = store.load()

    assert state.last_transaction_time == 999
    assert state.last_transaction_id == 42
