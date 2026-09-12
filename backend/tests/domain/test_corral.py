from datetime import UTC, datetime, timedelta

from app.domain.boosters import Booster
from app.domain.corral import Corral
from app.domain.player import Player


def test_start_work_sets_timestamps() -> None:
    corral = Corral("coop")

    corral.start_work(work_time_seconds=100)

    assert corral.work_start_timestamp is not None
    assert corral.work_end_timestamp is not None
    assert (corral.work_end_timestamp - corral.work_start_timestamp).total_seconds() == 100


def test_buy_animal_increments_amount() -> None:
    corral = Corral("coop")

    corral.buy_animal()
    corral.buy_animal()

    assert corral.animal_amount == 2


def test_upgrade_level_increments_level() -> None:
    corral = Corral("coop")

    corral.upgrade_level()

    assert corral.curlevel == 2


def test_reset_after_collect_clears_work_timestamps() -> None:
    corral = Corral("coop")
    corral.start_work(work_time_seconds=100)

    corral.reset_after_collect()

    assert corral.work_start_timestamp is None
    assert corral.work_end_timestamp is None


def test_requeue_is_noop_when_no_work_in_progress(player: Player) -> None:
    corral = Corral("coop")

    corral.requeue(player)

    assert corral.work_end_timestamp is None


def test_requeue_shortens_remaining_time_with_active_work_speed_booster(player: Player) -> None:
    corral = Corral("coop")
    corral.start_work(work_time_seconds=1000)
    player.active_boosters.work_speed = Booster(
        booster_type="WorkSpeed", percentage=50, time=100, activate_timestamp=datetime.now(UTC)
    )
    work_end_before = corral.work_end_timestamp
    assert work_end_before is not None

    corral.requeue(player)

    assert corral.work_end_timestamp is not None
    assert corral.work_end_timestamp < work_end_before
    assert abs((work_end_before - corral.work_end_timestamp) - timedelta(seconds=50)) < timedelta(seconds=1)
