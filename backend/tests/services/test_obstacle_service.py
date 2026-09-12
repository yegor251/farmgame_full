from app.domain.game import Game
from app.errors import GameErrorCode
from app.services import obstacle_service


def test_place_obstacle_unsafe_marks_all_covered_tiles_occupied() -> None:
    game = Game(tg_id=1, ref_id=0)

    obstacle_service.place_obstacle_unsafe(game, 5, 5, "tree")

    assert game.world.get_building(5, 5) is not None
    assert game.world.tile_array[5][5].occupied is True


def test_remove_obstacle_rejects_empty_tile() -> None:
    game = Game(tg_id=1, ref_id=0)

    assert obstacle_service.remove_obstacle(game, 5, 5) == GameErrorCode.BUILDING_NOT_PLACED


def test_remove_obstacle_rejects_non_obstacle_building() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.world.place_new("garden", 5, 5, (1, 1))

    assert obstacle_service.remove_obstacle(game, 5, 5) == GameErrorCode.SOCKET_UNKNOWN


def test_remove_obstacle_rejects_when_not_enough_money() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.money = 0
    obstacle_service.place_obstacle_unsafe(game, 5, 5, "tree")

    assert obstacle_service.remove_obstacle(game, 5, 5) == GameErrorCode.NOT_ENOUGH_MONEY


def test_remove_obstacle_charges_player_and_frees_tiles_on_success() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.money = 100
    obstacle_service.place_obstacle_unsafe(game, 5, 5, "tree")

    result = obstacle_service.remove_obstacle(game, 5, 5)

    assert result == GameErrorCode.OK
    assert game.player.money == 70
    assert game.world.get_building(5, 5) is None
    assert game.world.tile_array[5][5].occupied is False
