from datetime import UTC, datetime

from app.domain.boosters import Booster
from app.domain.garden import Garden
from app.domain.obstacle import Obstacle
from app.domain.player import Player
from app.domain.world import World
from app.errors import GameErrorCode


def test_inside_boundaries_true_within_grid() -> None:
    world = World()

    assert world.inside_boundaries(0, 0) is True
    assert world.inside_boundaries(world.size_x - 1, world.size_y - 1) is True


def test_inside_boundaries_false_outside_grid() -> None:
    world = World()

    assert world.inside_boundaries(-1, 0) is False
    assert world.inside_boundaries(0, world.size_y) is False


def test_validate_place_rejects_out_of_bounds_origin() -> None:
    world = World()

    assert world.validate_place(-1, 0, (1, 1)) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_validate_place_rejects_footprint_overflowing_the_grid() -> None:
    world = World()

    result = world.validate_place(world.size_x - 1, 0, (2, 2))

    assert result == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_validate_place_rejects_occupied_tile() -> None:
    world = World()
    world.place_new("garden", 5, 5, (1, 1))

    assert world.validate_place(5, 5, (1, 1)) == GameErrorCode.NOT_ABLE_TO_PLACE


def test_validate_place_accepts_free_tile() -> None:
    world = World()

    assert world.validate_place(5, 5, (1, 1)) == GameErrorCode.OK


def test_place_new_marks_footprint_occupied() -> None:
    world = World()

    result = world.place_new("bakery", 0, 0, (3, 2))

    assert result == GameErrorCode.OK
    for x in range(3):
        for y in range(2):
            assert world.tile_array[x][y].is_occupied() is True
    assert world.get_building(0, 0) is not None
    assert world.get_building(1, 0) is None


def test_remove_building_clears_footprint() -> None:
    world = World()
    world.place_new("bakery", 0, 0, (3, 2))

    world.remove_building(0, 0, (3, 2))

    assert world.get_building(0, 0) is None
    for x in range(3):
        for y in range(2):
            assert world.tile_array[x][y].is_occupied() is False


def test_get_building_returns_none_for_empty_tile() -> None:
    world = World()

    assert world.get_building(2, 2) is None


def test_validate_use_ok_for_occupied_tile_and_error_for_empty() -> None:
    world = World()
    world.place_new("garden", 1, 1, (1, 1))

    assert world.validate_use(1, 1) == GameErrorCode.OK
    assert world.validate_use(2, 2) == GameErrorCode.BUILDING_NOT_PLACED


def test_move_building_rejects_out_of_bounds_destination() -> None:
    world = World()
    world.place_new("garden", 1, 1, (1, 1))

    result = world.move_building(1, 1, world.size_x, 1)

    assert result == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_move_building_rejects_missing_source_building() -> None:
    world = World()

    assert world.move_building(1, 1, 2, 2) == GameErrorCode.BUILDING_NOT_PLACED


def test_move_building_rejects_obstacles() -> None:
    world = World()
    world.tile_array[1][1].place = Obstacle("stone_small")
    world.tile_array[1][1].occupied = True

    result = world.move_building(1, 1, 2, 2)

    assert result == GameErrorCode.CANT_MOVE_OBSTACLE


def test_move_building_succeeds_to_free_destination() -> None:
    world = World()
    world.place_new("garden", 1, 1, (1, 1))
    building = world.get_building(1, 1)

    result = world.move_building(1, 1, 4, 4)

    assert result == GameErrorCode.OK
    assert world.get_building(1, 1) is None
    assert world.get_building(4, 4) is building
    assert world.tile_array[4][4].is_occupied() is True


def test_move_building_reverts_when_destination_occupied() -> None:
    world = World()
    world.place_new("garden", 1, 1, (1, 1))
    world.place_new("garden", 4, 4, (1, 1))
    original_building = world.get_building(1, 1)

    result = world.move_building(1, 1, 4, 4)

    assert result == GameErrorCode.NOT_ABLE_TO_PLACE
    assert world.get_building(1, 1) is original_building
    assert world.tile_array[1][1].is_occupied() is True


def test_requeue_all_applies_active_booster_to_every_placed_building(player: Player) -> None:
    world = World()
    world.place_new("garden", 1, 1, (1, 1))
    garden = world.get_building(1, 1)
    assert isinstance(garden, Garden)
    garden.plant("wheat", 1000, booster_percentage=0)
    player.active_boosters.work_speed = Booster(
        booster_type="WorkSpeed", percentage=50, time=200, activate_timestamp=datetime.now(UTC)
    )
    grow_timestamp_before = garden.grow_timestamp

    result = world.requeue_all(player)

    assert result == GameErrorCode.OK
    assert garden.grow_timestamp < grow_timestamp_before
