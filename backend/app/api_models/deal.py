from pydantic import Field

from app.api_models.base import ResponseModel
from app.api_models.boosters import BoosterShelfResponse


class RewardResponse(ResponseModel):
    money: int | None = None
    token: int | None = None
    boosters: list[BoosterShelfResponse] | None = None


class DealResponse(ResponseModel):
    name: str
    ton_price: int | None = Field(default=None, alias="tonPrice")
    token_price: int | None = Field(default=None, alias="tokenPrice")
    usdt_price: int | None = Field(default=None, alias="usdtPrice")
    reward: RewardResponse
