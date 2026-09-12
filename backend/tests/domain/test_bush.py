from datetime import UTC, datetime, timedelta

from app.domain.boosters import Booster
from app.domain.bush import Bush
from app.domain.player import Player


def test_constructor_sets_ready_timestamp_from_speed() -> None:
    bush = Bush("cherry", speed_seconds=100)

    assert bush.get_name() == "cherry"
    assert bush.collected_amount == 0
    assert (bush.ready_timestamp - bush.last_time_collected).total_seconds() == 100


def test_record_collect_increments_amount_and_reschedules() -> None:
    bush = Bush("cherry", speed_seconds=100)

    bush.record_collect(speed_seconds=100, boosted_time=20)

    assert bush.collected_amount == 1
    assert (bush.ready_timestamp - bush.last_time_collected).total_seconds() == 80


def test_reset_after_payout_clears_collected_amount() -> None:
    bush = Bush("cherry", speed_seconds=100)
    bush.record_collect(speed_seconds=100, boosted_time=0)

    bush.reset_after_payout()

    assert bush.collected_amount == 0


def test_requeue_is_noop_without_active_work_speed_booster(player: Player) -> None:
    bush = Bush("cherry", speed_seconds=1000)
    ready_timestamp_before = bush.ready_timestamp

    bush.requeue(player)

    assert bush.ready_timestamp == ready_timestamp_before


def test_requeue_shortens_remaining_time_with_active_work_speed_booster(player: Player) -> None:
    bush = Bush("cherry", speed_seconds=1000)
    player.active_boosters.work_speed = Booster(
        booster_type="WorkSpeed", percentage=50, time=100, activate_timestamp=datetime.now(UTC)
    )
    ready_timestamp_before = bush.ready_timestamp

    bush.requeue(player)

    assert bush.ready_timestamp < ready_timestamp_before
    assert abs((ready_timestamp_before - bush.ready_timestamp) - timedelta(seconds=50)) < timedelta(seconds=1)
