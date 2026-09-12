from pydantic import Field

from app.api_models.base import ResponseModel
from app.api_models.item_container import ItemsContainerResponse
from app.api_models.order import OrderResponse
from app.api_models.spin import SpinResponse


class PlayerResponse(ResponseModel):
    money: int
    networth: int
    inventory: ItemsContainerResponse = Field(alias="Inventory")
    spin: SpinResponse | None = None
    orders: list[OrderResponse] | None = None
