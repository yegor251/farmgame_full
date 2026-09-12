from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.domain.buildable import Buildable
from app.errors import GameErrorCode

if TYPE_CHECKING:
    from app.domain.player import Player


class Garden(Buildable):
    def __init__(self) -> None:
        self.curplant: str | None = None
        self.plant_timestamp = datetime.now(UTC)
        self.grow_timestamp = datetime.now(UTC)

    def get_name(self) -> str:
        return "garden"

    def plant(self, new_plant: str, time_to_grow: int, booster_percentage: int) -> int:
        self.curplant = new_plant
        self.plant_timestamp = datetime.now(UTC)
        seconds = round(time_to_grow * (1 - booster_percentage * 0.01))
        self.grow_timestamp = self.plant_timestamp + timedelta(seconds=seconds)
        return GameErrorCode.OK

    def collect_state(self) -> int:
        now = datetime.now(UTC)
        self.curplant = None
        self.plant_timestamp = now
        self.grow_timestamp = now
        return GameErrorCode.OK

    def requeue(self, player: "Player") -> None:
        from app.domain import boosters

        booster_percentage, booster_time = boosters.get_info(player.active_boosters.work_speed)
        time_to_finish = max(int((self.grow_timestamp - datetime.now(UTC)).total_seconds()), 0)

        boosted_time = (
            round(booster_time * booster_percentage / 100)
            if time_to_finish > booster_time
            else round(time_to_finish * booster_percentage / 100)
        )
        self.grow_timestamp -= timedelta(seconds=boosted_time)
