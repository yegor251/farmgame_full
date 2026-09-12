from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.transfer_info import Withdraw
from app.persistence.models import Base, DepositRow, UserRow
from app.persistence.repository import (
    SqlDepositRepository,
    SqlUserRepository,
    SqlWithdrawRepository,
)


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


async def test_player_by_id_returns_none_when_missing(session: AsyncSession) -> None:
    repository = SqlUserRepository(session)

    assert await repository.player_by_id(1) is None


async def test_player_by_id_returns_record_when_present(session: AsyncSession) -> None:
    session.add(UserRow(user_id=1, ref_id=0, active=False))
    await session.commit()
    repository = SqlUserRepository(session)

    record = await repository.player_by_id(1)

    assert record is not None
    assert record.user_id == 1
    assert record.ref_id == 0
    assert record.active is False


async def test_activate_user_by_id_marks_user_active(session: AsyncSession) -> None:
    session.add(UserRow(user_id=1, ref_id=0, active=False))
    await session.commit()
    repository = SqlUserRepository(session)

    assert await repository.activate_user_by_id(1) is True

    record = await repository.player_by_id(1)
    assert record is not None
    assert record.active is True


async def test_get_deposits_by_user_id_returns_only_active_deposits(session: AsyncSession) -> None:
    session.add_all(
        [
            DepositRow(
                transaction_id=1,
                active=True,
                tg_id=42,
                amount=100,
                time_stamp=1000,
                jetton_signature="sig-1",
                commentary="",
            ),
            DepositRow(
                transaction_id=2,
                active=False,
                tg_id=42,
                amount=200,
                time_stamp=2000,
                jetton_signature="sig-2",
                commentary="",
            ),
        ]
    )
    await session.commit()
    repository = SqlDepositRepository(session)

    deposits = await repository.get_deposits_by_user_id(42)

    assert [d.transaction_id for d in deposits] == [1]


async def test_close_deposit_by_transaction_id_deactivates_deposit(session: AsyncSession) -> None:
    session.add(
        DepositRow(
            transaction_id=1,
            active=True,
            tg_id=42,
            amount=100,
            time_stamp=1000,
            jetton_signature="sig-1",
            commentary="",
        )
    )
    await session.commit()
    repository = SqlDepositRepository(session)

    assert await repository.close_deposit_by_transaction_id(1) is True

    deposits = await repository.get_deposits_by_user_id(42)
    assert deposits == []


async def test_check_withdraw_by_info_returns_none_when_missing(session: AsyncSession) -> None:
    repository = SqlWithdrawRepository(session)

    assert await repository.check_withdraw_by_info(1) is None


async def test_register_withdraw_persists_and_can_be_read_back(session: AsyncSession) -> None:
    repository = SqlWithdrawRepository(session)
    withdraw = Withdraw(
        transaction_id=1, status=0, tg_id=42, wallet="EQwallet", amount=500, time_stamp=1000
    )

    assert await repository.register_withdraw(withdraw) is True

    stored = await repository.check_withdraw_by_info(1)
    assert stored is not None
    assert stored.tg_id == 42
    assert stored.wallet == "EQwallet"
    assert stored.amount == 500
