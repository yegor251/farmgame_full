from pydantic import Field

from app.api_models.base import ResponseModel


class SlotResponse(ResponseModel):
    item: str
    amount: int


class SpinResponse(ResponseModel):
    items: list[SlotResponse]
    drop: SlotResponse
    generate_time_stamp: int = Field(alias="generateTimeStamp")
    activated: bool
