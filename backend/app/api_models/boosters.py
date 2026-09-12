from pydantic import Field

from app.api_models.base import ResponseModel


class ActiveBoosterResponse(ResponseModel):
    percentage: int
    time: int
    activate_time_stamp: int = Field(alias="activateTimeStamp")


class ActiveBoostersResponse(ResponseModel):
    order_money: ActiveBoosterResponse | None = Field(default=None, alias="OrderMoney")
    order_items: ActiveBoosterResponse | None = Field(default=None, alias="OrderItems")
    work_speed: ActiveBoosterResponse | None = Field(default=None, alias="WorkSpeed")
    grow_speed: ActiveBoosterResponse | None = Field(default=None, alias="GrowSpeed")


class BoosterShelfResponse(ResponseModel):
    booster_type: str = Field(alias="boosterType")
    percentage: int
    time: int
