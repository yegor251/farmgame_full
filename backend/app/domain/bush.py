from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.domain.buildable import Buildable

if TYPE_CHECKING:
    from app.domain.player import Player


class Bush(Buildable):
    def __init__(self, name: str, speed_seconds: int) -> None:
        self.bush_type = name
        self.last_time_collected = datetime.now(UTC)
        self.ready_timestamp = self.last_time_collected + timedelta(seconds=speed_seconds)
        self.collected_amount = 0

    def get_name(self) -> str:
        return self.bush_type

    def record_collect(self, speed_seconds: int, boosted_time: int) -> None:
        self.collected_amount += 1
        self.last_time_collected = datetime.now(UTC)
        self.ready_timestamp = self.last_time_collected + timedelta(seconds=speed_seconds - boosted_time)

    def reset_after_payout(self) -> None:
        self.collected_amount = 0

    def requeue(self, player: "Player") -> None:
        from app.domain import boosters

        booster_percentage, booster_time = boosters.get_info(player.active_boosters.work_speed)
        time_to_finish = max(int((self.ready_timestamp - datetime.now(UTC)).total_seconds()), 0)

        boosted_time = (
            round(booster_time * booster_percentage / 100)
            if time_to_finish > booster_time
            else round(time_to_finish * booster_percentage / 100)
        )
        self.ready_timestamp -= timedelta(seconds=boosted_time)
