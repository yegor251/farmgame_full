from typing import Any

from pydantic import Field

from app.api_models.base import ResponseModel
from app.api_models.boosters import ActiveBoostersResponse, BoosterShelfResponse
from app.api_models.deal import DealResponse
from app.api_models.player import PlayerResponse
from app.api_models.transaction import DepositResponse
from app.api_models.wallet import WalletResponse
from app.api_models.world import WorldResponse


class GameSessionResponse(ResponseModel):
    data_type: str = Field(alias="dataType")
    player: PlayerResponse
    world: WorldResponse | None = None
    deposits: list[DepositResponse] | None = None
    wallet: WalletResponse
    available_deals: dict[str, DealResponse] | None = Field(default=None, alias="availableDeals")
    available_boosters: list[BoosterShelfResponse] | None = Field(
        default=None, alias="availableBoosters"
    )
    active_boosters: ActiveBoostersResponse = Field(alias="activeBoosters")
    businesses: list[Any] = Field(default_factory=list)
    ref_amount: int = Field(alias="refAmount")


class OperationResponse(ResponseModel):
    data_type: str = Field(alias="dataType", default="result-code")
    code: int
