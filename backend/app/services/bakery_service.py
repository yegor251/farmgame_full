from datetime import UTC, datetime

from app.config import settings
from app.domain import boosters
from app.domain.bakery import Bakery
from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def use(bakery: Bakery, data: str, player: Player) -> int:
    bakery_info = get_catalog().bakeries[bakery.get_name()]
    work_type_info = bakery_info.work_types.get(data)
    if work_type_info is None:
        return GameErrorCode.SOCKET_WRONG_FORMAT

    validated = True
    for item, amount in work_type_info.items.items():
        if (player.inventory.get_amount(item) or 0) < amount:
            validated = False
    if bakery.curlevel < work_type_info.min_level:
        validated = False
    if bakery.last_empty_slot >= (bakery_info.max_slots + bakery.purchased_slots):
        validated = False

    if not validated:
        return GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS

    for item, amount in work_type_info.items.items():
        player.inventory.add_amount(item, -amount)

    booster_percentage, booster_time = boosters.get_info(player.active_boosters.work_speed)
    time_before_booster = max(int((bakery.last_end_time - datetime.now(UTC)).total_seconds()), 0)
    booster_time = max(booster_time - time_before_booster, 0)

    boosted_time = (
        round(booster_time * booster_percentage / 100)
        if work_type_info.time_to_finish > booster_time
        else round(work_type_info.time_to_finish * booster_percentage / 100)
    )
    bakery.add_slot(work_type_info, data, boosted_time)
    return GameErrorCode.OK


def collect(bakery: Bakery, player: Player) -> int:
    slot = bakery.slots[0] if bakery.slots else None
    if slot is None:
        return GameErrorCode.WORK_NOT_STARTED

    if slot.work_end_timestamp > datetime.now(UTC):
        return GameErrorCode.WORK_NOT_READY

    bakery_info = get_catalog().bakeries[bakery.get_name()]
    work_type_info = bakery_info.work_types[slot.name]
    if not player.inventory.check_map(work_type_info.products):
        return GameErrorCode.NO_SPACE_IN_INVENTORY

    player.inventory.add_map_unchecked(work_type_info.products)
    bakery.on_collect()
    bakery.slots.popleft()
    return GameErrorCode.OK


def upgrade(bakery: Bakery, player: Player) -> int:
    bakery_info = get_catalog().bakeries[bakery.get_name()]
    if bakery.curlevel >= bakery_info.max_level:
        return GameErrorCode.BUILDING_ALREADY_MAXXED_UP

    price = bakery_info.upgrades_price[bakery.curlevel - 1]
    if player.money < price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    for name in get_catalog().items_by_name_and_level(bakery.get_name(), bakery.curlevel + 1):
        player.inventory.add_amount(name, 0)
    player.money -= price
    bakery.upgrade_level()
    return GameErrorCode.OK


def purchase_slot(bakery: Bakery, player: Player) -> int:
    if bakery.purchased_slots >= settings.max_purchased_slots:
        return GameErrorCode.BUILDING_ALREADY_MAXXED_UP

    price = settings.purchased_slots_price[bakery.purchased_slots]
    if player.wallet.token_balance < price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    player.wallet.token_balance -= price
    bakery.purchased_slots += 1
    return GameErrorCode.OK
