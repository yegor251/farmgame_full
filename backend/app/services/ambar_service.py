from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def upgrade_inventory(player: Player) -> int:
    ambar_info = get_catalog().ambar
    level = player.inventory.level
    if level >= len(ambar_info.levels):
        return GameErrorCode.BUILDING_ALREADY_MAXXED_UP

    level_info = ambar_info.levels[level]
    if player.wallet.token_balance < level_info.price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    player.wallet.token_balance -= level_info.price
    player.inventory.enlarge_capacity(level_info.capacity_bonus)
    player.inventory.level += 1
    return GameErrorCode.OK
