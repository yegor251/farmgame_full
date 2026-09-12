from pydantic import Field

from app.api_models.base import ResponseModel


class WalletResponse(ResponseModel):
    usdt_balance: int = Field(alias="usdtBalance")
    ton_balance: int = Field(alias="tonBalance")
    token_balance: int = Field(alias="tokenBalance")
