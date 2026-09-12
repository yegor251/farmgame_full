from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.domain.buildable import Buildable

if TYPE_CHECKING:
    from app.domain.player import Player


class Corral(Buildable):
    def __init__(self, name: str) -> None:
        self.corral_type = name
        self.curlevel = 1
        self.work_start_timestamp: datetime | None = None
        self.work_end_timestamp: datetime | None = None
        self.animal_amount = 0

    def get_name(self) -> str:
        return self.corral_type

    def reset_after_collect(self) -> None:
        self.work_start_timestamp = None
        self.work_end_timestamp = None

    def start_work(self, work_time_seconds: int) -> None:
        self.work_start_timestamp = datetime.now(UTC)
        self.work_end_timestamp = self.work_start_timestamp + timedelta(seconds=work_time_seconds)

    def buy_animal(self) -> None:
        self.animal_amount += 1

    def upgrade_level(self) -> None:
        self.curlevel += 1

    def requeue(self, player: "Player") -> None:
        if self.work_end_timestamp is None:
            return
        from app.domain import boosters

        booster_percentage, booster_time = boosters.get_info(player.active_boosters.work_speed)
        time_to_finish = max(int((self.work_end_timestamp - datetime.now(UTC)).total_seconds()), 0)

        boosted_time = (
            round(booster_time * booster_percentage / 100)
            if time_to_finish > booster_time
            else round(time_to_finish * booster_percentage / 100)
        )
        self.work_end_timestamp -= timedelta(seconds=boosted_time)
