from typing import Annotated, Literal

from pydantic import BaseModel, Field


class SlotSnapshot(BaseModel):
    name: str
    start: int
    end: int


class GardenSnapshot(BaseModel):
    kind: Literal["garden"] = "garden"
    curplant: str | None
    plant_timestamp: int
    grow_timestamp: int


class BakerySnapshot(BaseModel):
    kind: Literal["bakery"] = "bakery"
    name: str
    curlevel: int
    slots: list[SlotSnapshot]
    last_empty_slot: int
    purchased_slots: int
    last_end_time: int


class CorralSnapshot(BaseModel):
    kind: Literal["corral"] = "corral"
    name: str
    curlevel: int
    work_start: int | None
    work_end: int | None
    animal_amount: int


class BushSnapshot(BaseModel):
    kind: Literal["bush"] = "bush"
    name: str
    last_time_collected: int
    ready_timestamp: int
    collected_amount: int


class ObstacleSnapshot(BaseModel):
    kind: Literal["obstacle"] = "obstacle"
    name: str


BuildableSnapshot = Annotated[
    GardenSnapshot | BakerySnapshot | CorralSnapshot | BushSnapshot | ObstacleSnapshot,
    Field(discriminator="kind"),
]


class PlacedBuildingSnapshot(BaseModel):
    x: int
    y: int
    building: BuildableSnapshot


class WorldSnapshot(BaseModel):
    buildings: list[PlacedBuildingSnapshot]


class ItemContainerSnapshot(BaseModel):
    items: dict[str, int]
    items_amount: int
    capacity: int
    level: int


class SpinSnapshot(BaseModel):
    items: list[tuple[str, int]]
    drop: tuple[str, int]
    activated: bool
    generate_timestamp: int


class OrderSnapshot(BaseModel):
    items: dict[str, int]
    price: int
    token_price: int
    completed: bool
    start_timestamp: int


class PlayerInfoSnapshot(BaseModel):
    money: int
    net_worth: int


class StatsSnapshot(BaseModel):
    orders_completed: int
    buildings_placed: dict[str, int]


class BoosterShelfSnapshot(BaseModel):
    booster_type: str
    percentage: int
    time: int


class DealsSnapshot(BaseModel):
    bought_deals: list[str]
    token_spent: int
    usdt_spent: int
    ton_spent: int
    boosters: list[BoosterShelfSnapshot]


class BoosterSnapshot(BaseModel):
    booster_type: str
    percentage: int
    time: int
    activate_timestamp: int


class ActiveBoostersSnapshot(BaseModel):
    order_money: BoosterSnapshot | None
    order_items: BoosterSnapshot | None
    work_speed: BoosterSnapshot | None
    grow_speed: BoosterSnapshot | None


class WalletSnapshot(BaseModel):
    token_balance: int
    usdt_balance: int
    ton_balance: int


class DepositSnapshot(BaseModel):
    transaction_id: int
    active: bool
    tg_id: int
    amount: int
    time_stamp: int
    jetton_signature: str
    commentary: str


class TransferInfoSnapshot(BaseModel):
    deposits: list[DepositSnapshot]


class ClientInfoSnapshot(BaseModel):
    tg_id: int
    ref_id: int
    banned: bool
    strikes: int
    referrals: list[int]
