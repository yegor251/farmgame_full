from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

BOOSTER_TYPES = ("OrderMoney", "OrderItems", "WorkSpeed", "GrowSpeed")


@dataclass
class Booster:
    booster_type: str
    percentage: int
    time: int
    activate_timestamp: datetime


@dataclass
class BoosterShelfEntry:
    booster_type: str
    percentage: int
    time: int


class ActiveBoosters:
    def __init__(self) -> None:
        self.order_money: Booster | None = None
        self.order_items: Booster | None = None
        self.work_speed: Booster | None = None
        self.grow_speed: Booster | None = None

    def get(self, booster_type: str) -> Booster | None:
        return {
            "OrderMoney": self.order_money,
            "OrderItems": self.order_items,
            "WorkSpeed": self.work_speed,
            "GrowSpeed": self.grow_speed,
        }[booster_type]

    def set(self, booster_type: str, booster: Booster | None) -> None:
        if booster_type == "OrderMoney":
            self.order_money = booster
        elif booster_type == "OrderItems":
            self.order_items = booster
        elif booster_type == "WorkSpeed":
            self.work_speed = booster
        elif booster_type == "GrowSpeed":
            self.grow_speed = booster


def check_booster(booster: Booster | None) -> bool:
    if booster is None:
        return False
    expires_at = booster.activate_timestamp + timedelta(seconds=booster.time)
    return expires_at >= datetime.now(UTC)


def renew_booster(booster: Booster | None) -> Booster | None:
    return booster if check_booster(booster) else None


def get_percentage(booster: Booster | None) -> int:
    renewed = renew_booster(booster)
    return renewed.percentage if renewed is not None else 0


def get_info(booster: Booster | None) -> tuple[int, int]:
    renewed = renew_booster(booster)
    if renewed is None:
        return (0, 0)
    expires_at = renewed.activate_timestamp + timedelta(seconds=renewed.time)
    remaining = int((expires_at - datetime.now(UTC)).total_seconds())
    return (renewed.percentage, remaining)


def regenerate(active_boosters: ActiveBoosters) -> None:
    active_boosters.order_money = renew_booster(active_boosters.order_money)
    active_boosters.order_items = renew_booster(active_boosters.order_items)
    active_boosters.work_speed = renew_booster(active_boosters.work_speed)
    active_boosters.grow_speed = renew_booster(active_boosters.grow_speed)


def activate(active_boosters: ActiveBoosters, shelf_entry: BoosterShelfEntry) -> None:
    booster = Booster(
        booster_type=shelf_entry.booster_type,
        percentage=shelf_entry.percentage,
        time=shelf_entry.time,
        activate_timestamp=datetime.now(UTC),
    )
    active_boosters.set(shelf_entry.booster_type, booster)
