from app.domain.garden import Garden
from app.domain.tile import Tile


def test_new_tile_is_unoccupied_and_empty() -> None:
    tile = Tile()

    assert tile.is_occupied() is False
    assert tile.place is None


def test_place_building_marks_occupied_and_creates_building() -> None:
    tile = Tile()

    tile.place_building("garden")

    assert tile.is_occupied() is True
    assert isinstance(tile.place, Garden)
