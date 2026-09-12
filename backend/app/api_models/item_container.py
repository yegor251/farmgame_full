from app.api_models.base import ResponseModel


class ItemsContainerResponse(ResponseModel):
    map: dict[str, int]
    level: int
