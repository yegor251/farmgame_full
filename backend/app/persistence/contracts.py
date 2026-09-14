from dataclasses import dataclass
from typing import Protocol

from app.domain.transfer_info import Deposit, Withdraw


@dataclass
class UserRecord:
    user_id: int
    ref_id: int
    active: bool


class UserRepository(Protocol):
    async def player_by_id(self, user_id: int) -> UserRecord | None: ...

    async def activate_user_by_id(self, user_id: int) -> bool: ...

    async def create_user(self, user_id: int, ref_id: int) -> bool: ...


class DepositRepository(Protocol):
    async def get_deposits_by_user_id(self, tg_id: int) -> list[Deposit]: ...

    async def close_deposit_by_transaction_id(self, transaction_id: int) -> bool: ...

    async def insert_deposit(self, deposit: Deposit) -> bool: ...


class WithdrawRepository(Protocol):
    async def check_withdraw_by_info(self, transaction_id: int) -> Withdraw | None: ...

    async def register_withdraw(self, withdraw: Withdraw) -> bool: ...

    async def list_pending_withdraws(self, limit: int) -> list[Withdraw]: ...

    async def mark_withdraw_sent(self, transaction_id: int) -> bool: ...
