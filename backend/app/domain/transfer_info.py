from dataclasses import dataclass, field


@dataclass
class Deposit:
    transaction_id: int
    active: bool
    tg_id: int
    amount: int
    time_stamp: int
    jetton_signature: str
    commentary: str


@dataclass
class Withdraw:
    transaction_id: int
    status: int
    tg_id: int
    wallet: str
    amount: int
    time_stamp: int


@dataclass
class TransferInfo:
    deposits: list[Deposit] = field(default_factory=list)
    withdraws: list[Withdraw] = field(default_factory=list)
