from app.config import settings
from app.domain.bakery import Bakery
from app.domain.bush import Bush
from app.domain.corral import Corral
from app.domain.garden import Garden
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import bakery_service, bush_service, corral_service, garden_service
from app.static_data.catalog import get_catalog


def building_exists(name: str) -> bool:
    return get_catalog().building_exists(name)


def get_size(name: str) -> tuple[int, int]:
    return get_catalog().building_size(name)


def get_map_limit(name: str) -> int:
    return get_catalog().building_map_limit(name)


def get_price(name: str) -> int:
    return get_catalog().building_price(name)


def get_items_by_name_and_level(name: str, level: int) -> set[str]:
    return get_catalog().items_by_name_and_level(name, level)


def verify_purchase(player: Player, building: str) -> int:
    catalog = get_catalog()
    building_type = catalog.building_type_by_name[building]
    price = get_price(building)
    placed_count = player.stats.buildings_placed[building]
    if building_type == "bakery":
        price = int(price * settings.building_bakery_per_building_k**placed_count)
    elif building_type == "garden":
        price = int(price * settings.building_garden_per_building_k**placed_count)
    elif building_type == "corral":
        price = int(price * settings.building_corral_per_building_k**placed_count)

    if player.money >= price:
        for name in get_items_by_name_and_level(building, 1):
            player.inventory.add_amount(name, 0)
        player.money -= price
        return GameErrorCode.OK
    return GameErrorCode.NOT_ENOUGH_MONEY


def use(player: Player, building: object, data: str) -> int:
    if isinstance(building, Garden):
        return garden_service.use(building, data, player)
    if isinstance(building, Bakery):
        return bakery_service.use(building, data, player)
    if isinstance(building, Bush):
        return bush_service.use(building, player, data)
    if isinstance(building, Corral):
        return corral_service.use(building, player, data)
    return GameErrorCode.SOCKET_WRONG_FORMAT


def collect(player: Player, building: object) -> int:
    if isinstance(building, Garden):
        return garden_service.collect(building, player)
    if isinstance(building, Bakery):
        return bakery_service.collect(building, player)
    if isinstance(building, Bush):
        return bush_service.collect(building, player)
    if isinstance(building, Corral):
        return corral_service.collect(building, player)
    return GameErrorCode.SOCKET_WRONG_FORMAT


def upgrade(player: Player, building: object) -> int:
    if isinstance(building, Bakery):
        return bakery_service.upgrade(building, player)
    if isinstance(building, Corral):
        return corral_service.upgrade(building, player)
    return GameErrorCode.SOCKET_WRONG_FORMAT


def purchase_slot(player: Player, building: object) -> int:
    if isinstance(building, Bakery):
        return bakery_service.purchase_slot(building, player)
    return GameErrorCode.SOCKET_WRONG_FORMAT
