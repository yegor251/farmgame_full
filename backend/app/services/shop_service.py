from app.domain.boosters import BoosterShelfEntry
from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def validate_purchase(player: Player, deal_name: str) -> int:
    if deal_name in player.deals.bought_deals:
        return GameErrorCode.DEAL_HAS_BEEN_ALREADY_BOUGHT

    deals = get_catalog().deals
    if deal_name not in deals:
        return GameErrorCode.SOCKET_WRONG_FORMAT

    deal = deals[deal_name]
    token_price = deal.token_price or 0
    ton_price = deal.ton_price or 0
    usdt_price = deal.usdt_price or 0

    if (
        player.wallet.token_balance < token_price
        or player.wallet.ton_balance < ton_price
        or player.wallet.usdt_balance < usdt_price
    ):
        return GameErrorCode.NOT_ENOUGH_MONEY

    player.wallet.token_balance -= token_price
    player.wallet.ton_balance -= ton_price
    player.wallet.usdt_balance -= usdt_price
    player.deals.token_spent += token_price
    player.deals.ton_spent += ton_price
    player.deals.usdt_spent += usdt_price
    return GameErrorCode.OK


def purchase_deal(player: Player, deal_name: str) -> int:
    validation_code = validate_purchase(player, deal_name)
    if validation_code == GameErrorCode.OK:
        deal = get_catalog().deals[deal_name]
        for booster in deal.reward.boosters or []:
            player.deals.boosters.insert(
                0, BoosterShelfEntry(booster.booster_type, booster.percentage, booster.time)
            )
        player.money += deal.reward.money or 0
        player.wallet.token_balance += deal.reward.token or 0
        player.deals.bought_deals.add(deal_name)
    return validation_code


def buy(name: str, amount: int, player: Player) -> int:
    catalog = get_catalog()
    plant = catalog.plants.get(name)
    if plant is None:
        return GameErrorCode.SOCKET_WRONG_FORMAT

    if amount <= 0:
        return GameErrorCode.INVALID_AMOUNT

    if player.money < amount * plant.seed.price:
        return GameErrorCode.NOT_ENOUGH_MONEY

    if not player.inventory.check_amount(amount):
        return GameErrorCode.NO_SPACE_IN_INVENTORY

    player.money -= amount * plant.seed.price
    player.inventory.add_amount(plant.name, amount)
    return GameErrorCode.OK
