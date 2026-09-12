from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.domain.buildable import Buildable
from app.static_data.models import WorkTypeInfo

if TYPE_CHECKING:
    from app.domain.player import Player


@dataclass
class Slot:
    name: str
    work_start_timestamp: datetime
    work_end_timestamp: datetime


def _make_slot(
    work_type: WorkTypeInfo | None,
    work_type_name: str,
    timestamp: datetime,
    boosted_time: int,
    end_timestamp: datetime | None = None,
) -> Slot:
    if work_type is None:
        assert end_timestamp is not None
        return Slot(work_type_name, timestamp, end_timestamp)
    seconds = work_type.time_to_finish - boosted_time
    return Slot(work_type_name, timestamp, timestamp + timedelta(seconds=seconds))


class Bakery(Buildable):
    def __init__(self, name: str) -> None:
        self.bakery_type = name
        self.curlevel = 1
        self.slots: deque[Slot] = deque()
        self.last_empty_slot = 0
        self.purchased_slots = 0
        self.last_end_time = datetime.now(UTC)

    def get_name(self) -> str:
        return self.bakery_type

    def on_collect(self) -> None:
        self.last_empty_slot -= 1

    def add_slot(self, work_type: WorkTypeInfo, work_type_name: str, boosted_time: int) -> None:
        now = datetime.now(UTC)
        timestamp = now
        if self.last_empty_slot > 0 and self.last_end_time >= now:
            timestamp = self.last_end_time
        slot = _make_slot(work_type, work_type_name, timestamp, boosted_time)
        self.last_end_time = slot.work_end_timestamp
        self.slots.append(slot)
        self.last_empty_slot += 1

    def upgrade_level(self) -> None:
        self.curlevel += 1

    def requeue(self, player: "Player") -> None:
        from app.domain import boosters
        from app.static_data.catalog import get_catalog

        booster_percentage, remaining_booster_time = boosters.get_info(player.active_boosters.work_speed)
        work_types = get_catalog().bakeries[self.get_name()].work_types

        new_slots: deque[Slot] = deque()
        current_end_time = datetime.now(UTC)

        for slot in self.slots:
            work_type_info = work_types[slot.name]
            original_time_to_finish = int(
                (slot.work_end_timestamp - slot.work_start_timestamp).total_seconds()
            )

            boosted_time = (
                round(remaining_booster_time * booster_percentage / 100)
                if original_time_to_finish > remaining_booster_time
                else round(original_time_to_finish * booster_percentage / 100)
            )
            remaining_booster_time = max(remaining_booster_time - original_time_to_finish, 0)

            new_start_time = slot.work_start_timestamp if not new_slots else current_end_time
            new_slot = _make_slot(work_type_info, slot.name, new_start_time, boosted_time)
            current_end_time = new_slot.work_end_timestamp
            new_slots.append(new_slot)

        self.slots = new_slots
        self.last_end_time = current_end_time
