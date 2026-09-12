from app.api_models.base import ResponseModel


class DepositResponse(ResponseModel):
    transaction_id: int
    active: bool
    tg_id: int
    amount: int
    time_stamp: int
    jetton_signature: str
    commentary: str


class WithdrawResponse(ResponseModel):
    transaction_id: int
    status: int
    tg_id: int
    wallet: str
    amount: int
    time_stamp: int
