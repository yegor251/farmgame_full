from datetime import UTC, datetime

from app.domain import boosters
from app.domain.garden import Garden
from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def use(garden: Garden, data: str, player: Player) -> int:
    catalog = get_catalog()
    if data not in catalog.plants:
        return GameErrorCode.SOCKET_WRONG_FORMAT

    if garden.curplant is not None:
        return GameErrorCode.CANNOT_USE_BUILDING

    if (player.inventory.get_amount(data) or 0) < 1:
        return GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS

    player.inventory.add_amount(data, -1)
    booster_percentage = boosters.get_percentage(player.active_boosters.grow_speed)
    seed = catalog.plants[data].seed
    garden.plant(data, seed.time_to_grow, booster_percentage)
    return GameErrorCode.OK


def collect(garden: Garden, player: Player) -> int:
    curplant = garden.curplant
    if curplant is None:
        return GameErrorCode.PLANT_NOT_PLANTED

    if garden.grow_timestamp >= datetime.now(UTC):
        return GameErrorCode.PLANT_NOT_GROWN

    grow_amount = get_catalog().plants[curplant].seed.amount
    if not player.inventory.check_amount(grow_amount):
        return GameErrorCode.NO_SPACE_IN_INVENTORY

    garden.collect_state()
    player.inventory.add_amount(curplant, grow_amount)
    return GameErrorCode.OK
