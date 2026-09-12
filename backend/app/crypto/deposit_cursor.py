from dataclasses import dataclass
from pathlib import Path


@dataclass
class DepositCursorState:
    last_transaction_time: int
    last_transaction_id: int


class DepositCursorStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> DepositCursorState:
        try:
            lines = self._path.read_text().splitlines()
            return DepositCursorState(
                last_transaction_time=int(lines[0].strip()) - 1,
                last_transaction_id=int(lines[1].strip()),
            )
        except (OSError, IndexError, ValueError):
            return DepositCursorState(last_transaction_time=0, last_transaction_id=0)

    def save(self, state: DepositCursorState) -> None:
        self._path.write_text(f"{state.last_transaction_time}\n{state.last_transaction_id}")
