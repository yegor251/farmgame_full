from pydantic import BaseModel, ConfigDict, Field


class StaticModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)


class SeedInfo(StaticModel):
    minimum_lvl: int = Field(alias="minimumLvl")
    price: int
    amount: int
    time_to_grow: int = Field(alias="timeToGrow")


class PlantInfo(StaticModel):
    name: str
    order_price: int = Field(alias="orderPrice")
    order_token_price: int = Field(alias="orderTokenPrice")
    order_amount_min: int = Field(alias="orderAmountMin")
    order_amount_max: int = Field(alias="orderAmountMax")
    seed: SeedInfo


class ItemInfo(StaticModel):
    name: str
    order_price: int = Field(alias="orderPrice")
    order_token_price: int = Field(alias="orderTokenPrice")
    order_amount_min: int = Field(alias="orderAmountMin")
    order_amount_max: int = Field(alias="orderAmountMax")


class GardenInfo(StaticModel):
    name: str
    price: int
    map_limit: int = Field(alias="mapLimit")


class WorkTypeInfo(StaticModel):
    min_level: int = Field(alias="minLevel")
    time_to_finish: int = Field(alias="timeToFinish")
    items: dict[str, int]
    products: dict[str, int]


class BakeryInfo(StaticModel):
    name: str
    price: int
    max_slots: int = Field(alias="maxSlots")
    sizex: int
    sizey: int
    max_level: int = Field(alias="maxLevel")
    map_limit: int = Field(alias="mapLimit")
    work_types: dict[str, WorkTypeInfo] = Field(alias="workTypes")
    upgrades_price: list[int] = Field(alias="upgradesPrice")


class CorralInfo(StaticModel):
    name: str
    price: int
    speed: int
    max_animal_amount: int = Field(alias="maxAnimalAmount")
    animal_price: int = Field(alias="animalPrice")
    sizex: int
    sizey: int
    max_level: int = Field(alias="maxLevel")
    map_limit: int = Field(alias="mapLimit")
    intake: dict[str, int]
    products: dict[str, int]
    upgrades_price: list[int] = Field(alias="upgradesPrice")


class BushInfo(StaticModel):
    name: str
    price: int
    product_limit: int = Field(alias="productLimit")
    speed: int
    sizex: int
    sizey: int
    map_limit: int = Field(alias="mapLimit")
    products: dict[str, int]


class ObstacleInfo(StaticModel):
    name: str
    remove_price: int | None = Field(default=None, alias="removePrice")
    remove_token_price: int | None = Field(default=None, alias="removeTokenPrice")
    sizex: int
    sizey: int


class AmbarLevelInfo(StaticModel):
    price: int
    capacity_bonus: int = Field(alias="capacityBonus")


class AmbarInfo(StaticModel):
    levels: list[AmbarLevelInfo]


class BoosterInfo(StaticModel):
    booster_type: str = Field(alias="boosterType")
    percentage: int
    time: int


class RewardInfo(StaticModel):
    money: int | None = None
    token: int | None = None
    boosters: list[BoosterInfo] | None = None


class DealInfo(StaticModel):
    name: str
    ton_price: int | None = Field(default=None, alias="tonPrice")
    token_price: int | None = Field(default=None, alias="tokenPrice")
    usdt_price: int | None = Field(default=None, alias="usdtPrice")
    reward: RewardInfo


class StartBuildInfo(StaticModel):
    name: str
    x: int
    y: int


class MapInfo(StaticModel):
    map: list[StartBuildInfo]
