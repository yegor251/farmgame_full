from pydantic import BaseModel, ConfigDict, Field


class TonApiAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")

    address: str


class TonTransferAction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    recipient: TonApiAddress
    amount: int
    comment: str = ""


class JettonInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    address: str


class JettonTransferAction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    recipient: TonApiAddress
    amount: int
    jetton: JettonInfo
    comment: str = ""


class EventAction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    TonTransfer: TonTransferAction | None = None
    JettonTransfer: JettonTransferAction | None = None


class AccountEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str
    timestamp: int
    actions: list[EventAction] = Field(default_factory=list)


class AccountEventsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    events: list[AccountEvent] = Field(default_factory=list)


class JettonBalanceResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    wallet_address: TonApiAddress
