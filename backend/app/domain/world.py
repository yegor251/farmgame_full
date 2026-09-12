from typing import TYPE_CHECKING

from app.config import settings
from app.domain.buildable import Buildable
from app.domain.tile import Tile
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog

if TYPE_CHECKING:
    from app.domain.player import Player


class World:
    def __init__(self) -> None:
        self.size_x = settings.map_size_x
        self.size_y = settings.map_size_y
        self.tile_array: list[list[Tile]] = [
            [Tile() for _ in range(self.size_y)] for _ in range(self.size_x)
        ]

    def _mark_occupied(self, x: int, y: int, size: tuple[int, int], occupied: bool) -> None:
        size_x, size_y = size
        for tx in range(size_x):
            for ty in range(size_y):
                self.tile_array[x + tx][y + ty].occupied = occupied

    def place_new(self, building_name: str, x: int, y: int, size: tuple[int, int]) -> int:
        self._mark_occupied(x, y, size, True)
        self.tile_array[x][y].place_building(building_name)
        return GameErrorCode.OK

    def place_existing(self, building: Buildable, x: int, y: int, size: tuple[int, int]) -> int:
        self._mark_occupied(x, y, size, True)
        self.tile_array[x][y].occupied = True
        self.tile_array[x][y].place = building
        return GameErrorCode.OK

    def remove_building(self, x: int, y: int, size: tuple[int, int]) -> None:
        self._mark_occupied(x, y, size, False)
        self.tile_array[x][y].place = None

    def move_building(self, x: int, y: int, to_x: int, to_y: int) -> int:
        if not (self.inside_boundaries(x, y) and self.inside_boundaries(to_x, to_y)):
            return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES

        building = self.tile_array[x][y].place
        if building is None:
            return GameErrorCode.BUILDING_NOT_PLACED

        if get_catalog().is_obstacle(building.get_name()):
            return GameErrorCode.CANT_MOVE_OBSTACLE

        size = get_catalog().building_size(building.get_name())
        self.remove_building(x, y, size)
        if self.validate_place(to_x, to_y, size) == GameErrorCode.OK:
            self.place_existing(building, to_x, to_y, size)
            return GameErrorCode.OK
        self.place_existing(building, x, y, size)
        return GameErrorCode.NOT_ABLE_TO_PLACE

    def get_building(self, x: int, y: int) -> Buildable | None:
        return self.tile_array[x][y].place

    def validate_place(self, x: int, y: int, size: tuple[int, int]) -> int:
        if not self.inside_boundaries(x, y):
            return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES
        size_x, size_y = size
        if x + size_x > self.size_x or y + size_y > self.size_y:
            return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES
        for tx in range(size_x):
            for ty in range(size_y):
                if self.tile_array[x + tx][y + ty].is_occupied():
                    return GameErrorCode.NOT_ABLE_TO_PLACE
        return GameErrorCode.OK

    def inside_boundaries(self, x: int, y: int) -> bool:
        return 0 <= x < self.size_x and 0 <= y < self.size_y

    def validate_use(self, x: int, y: int) -> int:
        if self.tile_array[x][y].is_occupied():
            return GameErrorCode.OK
        return GameErrorCode.BUILDING_NOT_PLACED

    def requeue_all(self, player: "Player") -> int:
        for column in self.tile_array:
            for tile in column:
                if tile.place is not None:
                    tile.place.requeue(player)
        return GameErrorCode.OK
