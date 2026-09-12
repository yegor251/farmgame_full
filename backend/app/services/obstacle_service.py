from typing import TYPE_CHECKING

from app.domain.obstacle import Obstacle
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog

if TYPE_CHECKING:
    from app.domain.game import Game


def remove_obstacle(game: "Game", x: int, y: int) -> int:
    building = game.world.get_building(x, y)
    if building is None:
        return GameErrorCode.BUILDING_NOT_PLACED

    catalog = get_catalog()
    if not catalog.is_obstacle(building.get_name()):
        return GameErrorCode.SOCKET_UNKNOWN

    obstacle_info = catalog.obstacles[building.get_name()]
    remove_price = obstacle_info.remove_price or 0
    remove_token_price = obstacle_info.remove_token_price or 0

    if game.player.money < remove_price or game.player.wallet.token_balance < remove_token_price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    game.player.money -= remove_price
    game.player.wallet.token_balance -= remove_token_price

    game.world.tile_array[x][y].place = None
    for i in range(x, x + obstacle_info.sizex):
        for j in range(y, y + obstacle_info.sizey):
            game.world.tile_array[i][j].occupied = False

    return GameErrorCode.OK


def place_obstacle_unsafe(game: "Game", x: int, y: int, obstacle_name: str) -> None:
    game.world.tile_array[x][y].place = Obstacle(obstacle_name)
    obstacle_info = get_catalog().obstacles[obstacle_name]
    for i in range(x, x + obstacle_info.sizex):
        for j in range(y, y + obstacle_info.sizey):
            game.world.tile_array[i][j].occupied = True
