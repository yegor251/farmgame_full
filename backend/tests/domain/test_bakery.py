from datetime import UTC, datetime, timedelta

from app.domain.bakery import Bakery
from app.domain.boosters import Booster
from app.domain.player import Player
from app.static_data.catalog import get_catalog
from app.static_data.models import WorkTypeInfo


def _bread_work_type() -> WorkTypeInfo:
    return WorkTypeInfo(min_level=1, time_to_finish=120, items={"wheat": 3}, products={"bread": 1})


def test_get_name_returns_bakery_type() -> None:
    assert Bakery("bakery").get_name() == "bakery"


def test_add_slot_schedules_from_now_when_no_pending_slots() -> None:
    bakery = Bakery("bakery")

    bakery.add_slot(_bread_work_type(), "bread", boosted_time=0)

    assert len(bakery.slots) == 1
    slot = bakery.slots[0]
    assert (slot.work_end_timestamp - slot.work_start_timestamp).total_seconds() == 120
    assert bakery.last_empty_slot == 1
    assert bakery.last_end_time == slot.work_end_timestamp


def test_add_slot_chains_after_pending_slot() -> None:
    bakery = Bakery("bakery")
    bakery.add_slot(_bread_work_type(), "bread", boosted_time=0)
    first_slot_end = bakery.slots[0].work_end_timestamp

    bakery.add_slot(_bread_work_type(), "bread", boosted_time=0)

    second_slot = bakery.slots[1]
    assert second_slot.work_start_timestamp == first_slot_end
    assert bakery.last_empty_slot == 2


def test_on_collect_decrements_last_empty_slot() -> None:
    bakery = Bakery("bakery")
    bakery.add_slot(_bread_work_type(), "bread", boosted_time=0)

    bakery.on_collect()

    assert bakery.last_empty_slot == 0


def test_upgrade_level_increments_level() -> None:
    bakery = Bakery("bakery")

    bakery.upgrade_level()

    assert bakery.curlevel == 2


def test_requeue_shortens_single_slot_using_catalog_work_type(player: Player) -> None:
    bakery = Bakery("bakery")
    bread_info = get_catalog().bakeries["bakery"].work_types["bread"]
    bakery.add_slot(bread_info, "bread", boosted_time=0)
    player.active_boosters.work_speed = Booster(
        booster_type="WorkSpeed", percentage=50, time=200, activate_timestamp=datetime.now(UTC)
    )

    bakery.requeue(player)

    slot = bakery.slots[0]
    assert (slot.work_end_timestamp - slot.work_start_timestamp) == timedelta(seconds=60)


def test_requeue_is_noop_without_active_booster(player: Player) -> None:
    bakery = Bakery("bakery")
    bread_info = get_catalog().bakeries["bakery"].work_types["bread"]
    bakery.add_slot(bread_info, "bread", boosted_time=0)
    duration_before = bakery.slots[0].work_end_timestamp - bakery.slots[0].work_start_timestamp

    bakery.requeue(player)

    duration_after = bakery.slots[0].work_end_timestamp - bakery.slots[0].work_start_timestamp
    assert duration_after == duration_before
