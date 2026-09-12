from datetime import UTC, datetime

from app.domain import boosters
from app.domain.corral import Corral
from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def get_time_to_finish(speed: int, level: int) -> int:
    return round(speed * (1 - 0.1 * (level - 1)))


def buy_animal(corral: Corral, player: Player) -> int:
    corral_info = get_catalog().corrals[corral.get_name()]
    if corral.animal_amount >= corral_info.max_animal_amount:
        return GameErrorCode.CORRAL_ALREADY_MAX_ANIMALS

    if player.money < corral_info.animal_price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    player.money -= corral_info.animal_price
    corral.buy_animal()
    return GameErrorCode.OK


def start_work(corral: Corral, player: Player) -> int:
    corral_info = get_catalog().corrals[corral.get_name()]

    if corral.work_end_timestamp is not None:
        return GameErrorCode.WORK_NOT_READY

    for item, amount in corral_info.intake.items():
        if (player.inventory.get_amount(item) or 0) < amount * corral.animal_amount:
            return GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS

    for item, amount in corral_info.intake.items():
        player.inventory.add_amount(item, -amount * corral.animal_amount)

    booster_percentage, booster_time = boosters.get_info(player.active_boosters.work_speed)
    time_to_finish = get_time_to_finish(corral_info.speed, corral.curlevel)
    boosted_time = (
        round(booster_time * booster_percentage / 100)
        if time_to_finish > booster_time
        else round(time_to_finish * booster_percentage / 100)
    )
    corral.start_work(time_to_finish - boosted_time)
    return GameErrorCode.OK


def use(corral: Corral, player: Player, data: str) -> int:
    if data == "buy":
        return buy_animal(corral, player)
    if data == "start":
        return start_work(corral, player)
    return GameErrorCode.SOCKET_WRONG_FORMAT


def collect(corral: Corral, player: Player) -> int:
    if corral.work_start_timestamp is None:
        return GameErrorCode.WORK_NOT_STARTED

    assert corral.work_end_timestamp is not None
    if corral.work_end_timestamp >= datetime.now(UTC):
        return GameErrorCode.WORK_NOT_READY

    corral_info = get_catalog().corrals[corral.get_name()]
    products = {name: amount * corral.animal_amount for name, amount in corral_info.products.items()}
    if not player.inventory.check_map(products):
        return GameErrorCode.NO_SPACE_IN_INVENTORY

    player.inventory.add_map_unchecked(products)
    corral.reset_after_collect()
    return GameErrorCode.OK


def upgrade(corral: Corral, player: Player) -> int:
    corral_info = get_catalog().corrals[corral.get_name()]
    if corral.curlevel >= corral_info.max_level:
        return GameErrorCode.BUILDING_ALREADY_MAXXED_UP

    price = corral_info.upgrades_price[corral.curlevel - 1]
    if player.money <= price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    corral.upgrade_level()
    return GameErrorCode.OK
