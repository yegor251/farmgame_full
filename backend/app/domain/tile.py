from app.domain.buildable import Buildable
from app.domain.building_factory import create_building


class Tile:
    def __init__(self) -> None:
        self.occupied = False
        self.place: Buildable | None = None

    def place_building(self, building_name: str) -> None:
        self.occupied = True
        self.place = create_building(building_name)

    def is_occupied(self) -> bool:
        return self.occupied
