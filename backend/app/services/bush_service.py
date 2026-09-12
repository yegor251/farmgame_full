from datetime import UTC, datetime

from app.domain import boosters
from app.domain.bush import Bush
from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def use(bush: Bush, player: Player, data: str) -> int:
    bush_info = get_catalog().bushes[bush.get_name()]
    new_price = round(bush_info.price * 1.5)

    if bush.collected_amount < bush_info.product_limit:
        return GameErrorCode.BUSH_NOT_EXPIRED

    if player.money <= new_price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    player.money -= new_price
    bush.reset_after_payout()
    return GameErrorCode.OK


def collect(bush: Bush, player: Player) -> int:
    bush_info = get_catalog().bushes[bush.get_name()]

    if bush.ready_timestamp >= datetime.now(UTC):
        return GameErrorCode.WORK_NOT_READY

    if bush.collected_amount >= bush_info.product_limit:
        return GameErrorCode.BUSH_EXPIRED

    if not player.inventory.check_map(bush_info.products):
        return GameErrorCode.NO_SPACE_IN_INVENTORY

    player.inventory.add_map_unchecked(bush_info.products)

    booster_percentage, booster_time = boosters.get_info(player.active_boosters.grow_speed)
    time_to_finish = bush_info.speed
    boosted_time = (
        round(booster_time * booster_percentage / 100)
        if time_to_finish > booster_time
        else round(time_to_finish * booster_percentage / 100)
    )
    bush.record_collect(bush_info.speed, boosted_time)
    return GameErrorCode.OK
