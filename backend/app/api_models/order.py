from pydantic import Field

from app.api_models.base import ResponseModel


class OrderResponse(ResponseModel):
    order_items: dict[str, int] = Field(alias="orderItems")
    order_price: int = Field(alias="orderPrice")
    order_token_price: int = Field(alias="orderTokenPrice")
    completed: bool
    time_stamp: int = Field(alias="timeStamp")
