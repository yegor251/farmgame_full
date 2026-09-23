from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ref_id: Mapped[int] = mapped_column(BigInteger)
    active: Mapped[bool] = mapped_column(Boolean)


class DepositRow(Base):
    __tablename__ = "deposits"

    transaction_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[int] = mapped_column(BigInteger)
    time_stamp: Mapped[int] = mapped_column(BigInteger)
    jetton_signature: Mapped[str] = mapped_column(String)
    commentary: Mapped[str] = mapped_column(String)
