from pydantic import Field

from app.api_models.base import ResponseModel


class BuildingSlotResponse(ResponseModel):
    work_name: str | None = Field(default=None, alias="workName")
    work_start_time_stamp: int = Field(alias="workStartTimeStamp")
    work_end_time_stamp: int = Field(alias="workEndTimeStamp")


class BuildingResponse(ResponseModel):
    name: str
    x: int
    y: int
    slots: list[BuildingSlotResponse]
    integer_data: int | None = Field(default=None, alias="integerData")
    level: int | None = None


class WorldResponse(ResponseModel):
    tile_array: list[BuildingResponse] = Field(alias="tileArray")
