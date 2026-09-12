from datetime import UTC, datetime, timedelta

from app.domain.boosters import Booster
from app.domain.garden import Garden
from app.domain.player import Player
from app.errors import GameErrorCode


def test_plant_sets_curplant_and_grow_timestamp() -> None:
    garden = Garden()

    result = garden.plant("wheat", 100, booster_percentage=0)

    assert result == GameErrorCode.OK
    assert garden.curplant == "wheat"
    assert garden.grow_timestamp > garden.plant_timestamp


def test_plant_shortens_grow_time_with_booster_percentage() -> None:
    garden = Garden()

    garden.plant("wheat", 100, booster_percentage=50)

    grow_seconds = (garden.grow_timestamp - garden.plant_timestamp).total_seconds()
    assert grow_seconds == 50


def test_collect_state_resets_garden() -> None:
    garden = Garden()
    garden.plant("wheat", 100, booster_percentage=0)

    result = garden.collect_state()

    assert result == GameErrorCode.OK
    assert garden.curplant is None


def test_requeue_is_noop_without_active_work_speed_booster(player: Player) -> None:
    garden = Garden()
    garden.plant("wheat", 1000, booster_percentage=0)
    grow_timestamp_before = garden.grow_timestamp

    garden.requeue(player)

    assert garden.grow_timestamp == grow_timestamp_before


def test_requeue_shortens_remaining_time_with_active_work_speed_booster(player: Player) -> None:
    garden = Garden()
    garden.plant("wheat", 1000, booster_percentage=0)
    player.active_boosters.work_speed = Booster(
        booster_type="WorkSpeed", percentage=50, time=100, activate_timestamp=datetime.now(UTC)
    )
    grow_timestamp_before = garden.grow_timestamp

    garden.requeue(player)

    assert garden.grow_timestamp < grow_timestamp_before
    assert abs((grow_timestamp_before - garden.grow_timestamp) - timedelta(seconds=50)) < timedelta(seconds=1)
