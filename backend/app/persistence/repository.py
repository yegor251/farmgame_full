import logging

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.transfer_info import Deposit
from app.persistence.contracts import UserRecord
from app.persistence.models import DepositRow, UserRow

logger = logging.getLogger(__name__)


class SqlUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def player_by_id(self, user_id: int) -> UserRecord | None:
        try:
            row = await self._session.get(UserRow, user_id)
        except SQLAlchemyError:
            logger.exception("Occured while finding user %s", user_id)
            return None
        if row is None:
            return None
        return UserRecord(user_id=row.user_id, ref_id=row.ref_id, active=row.active)

    async def activate_user_by_id(self, user_id: int) -> bool:
        try:
            await self._session.execute(
                update(UserRow).where(UserRow.user_id == user_id).values(active=True)
            )
            await self._session.commit()
        except SQLAlchemyError:
            logger.exception("Occured while trying to activate user(%s)", user_id)
            return False
        return True

    async def create_user(self, user_id: int, ref_id: int) -> bool:
        try:
            self._session.add(UserRow(user_id=user_id, ref_id=ref_id, active=False))
            await self._session.commit()
        except SQLAlchemyError:
            logger.exception("Occured while trying to create user(%s, %s)", user_id, ref_id)
            await self._session.rollback()
            return False
        return True


class SqlDepositRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_deposits_by_user_id(self, tg_id: int) -> list[Deposit]:
        try:
            result = await self._session.execute(
                select(DepositRow).where(DepositRow.tg_id == tg_id, DepositRow.active.is_(True))
            )
            rows = result.scalars().all()
        except SQLAlchemyError:
            logger.exception("Occured while trying to find user's deposits(%s)", tg_id)
            return []
        return [
            Deposit(
                transaction_id=row.transaction_id,
                active=row.active,
                tg_id=row.tg_id,
                amount=row.amount,
                time_stamp=row.time_stamp,
                jetton_signature=row.jetton_signature,
                commentary=row.commentary,
            )
            for row in rows
        ]

    async def close_deposit_by_transaction_id(self, transaction_id: int) -> bool:
        try:
            await self._session.execute(
                update(DepositRow)
                .where(DepositRow.transaction_id == transaction_id)
                .values(active=False)
            )
            await self._session.commit()
        except SQLAlchemyError:
            logger.exception("Occured while trying to deactivate transaction(%s)", transaction_id)
            return False
        return True

    async def insert_deposit(self, deposit: Deposit) -> bool:
        try:
            self._session.add(
                DepositRow(
                    transaction_id=deposit.transaction_id,
                    active=deposit.active,
                    tg_id=deposit.tg_id,
                    amount=deposit.amount,
                    time_stamp=deposit.time_stamp,
                    jetton_signature=deposit.jetton_signature,
                    commentary=deposit.commentary,
                )
            )
            await self._session.commit()
        except SQLAlchemyError:
            logger.exception("Occured while trying to INSERT deposit(%s)", deposit.transaction_id)
            await self._session.rollback()
            return False
        return True
