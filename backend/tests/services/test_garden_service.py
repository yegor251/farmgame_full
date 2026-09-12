from datetime import UTC, datetime, timedelta

from app.domain.garden import Garden
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import garden_service


def test_use_rejects_unknown_seed() -> None:
    player = Player()
    garden = Garden()

    assert garden_service.use(garden, "not-a-seed", player) == GameErrorCode.SOCKET_WRONG_FORMAT


def test_use_rejects_when_garden_already_has_a_plant() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 5)
    garden = Garden()
    garden.plant("wheat", 60, 0)

    assert garden_service.use(garden, "wheat", player) == GameErrorCode.CANNOT_USE_BUILDING


def test_use_rejects_when_not_enough_seeds_in_inventory() -> None:
    player = Player()
    garden = Garden()

    assert garden_service.use(garden, "wheat", player) == GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS


def test_use_plants_and_deducts_one_seed_on_success() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 5)
    garden = Garden()

    result = garden_service.use(garden, "wheat", player)

    assert result == GameErrorCode.OK
    assert garden.curplant == "wheat"
    assert player.inventory.items["wheat"] == 4


def test_collect_rejects_unplanted_garden() -> None:
    player = Player()
    garden = Garden()

    assert garden_service.collect(garden, player) == GameErrorCode.PLANT_NOT_PLANTED


def test_collect_rejects_when_not_grown_yet() -> None:
    player = Player()
    garden = Garden()
    garden.plant("wheat", 3600, 0)

    assert garden_service.collect(garden, player) == GameErrorCode.PLANT_NOT_GROWN


def test_collect_adds_yield_and_resets_garden_when_grown() -> None:
    player = Player()
    garden = Garden()
    garden.plant("wheat", 60, 0)
    garden.grow_timestamp = datetime.now(UTC) - timedelta(seconds=1)

    result = garden_service.collect(garden, player)

    assert result == GameErrorCode.OK
    assert garden.curplant is None
    assert player.inventory.items["wheat"] == 3
