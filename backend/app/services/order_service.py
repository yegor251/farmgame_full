import math
import random
from datetime import UTC, datetime, timedelta

from app.config import settings
from app.domain import boosters
from app.domain.orders import Order
from app.domain.player import Player
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def get_orders_amount(player: Player) -> int:
    if player.net_worth <= 0:
        return 1
    return int(math.log(player.net_worth) / math.log(5)) + 1


def get_key_set_size(player: Player) -> int:
    return int(min(8, math.sqrt(2 * len(player.inventory.items))))


def generate_order(player: Player, timestamp: datetime) -> Order:
    try:
        key_set_size = get_key_set_size(player)
        items_amount = random.randint(0, max(key_set_size - 1, 0)) + 1
        keyset = player.inventory.pull_random_unique(items_amount)
        price_modifier = random.random() * 0.6 + 0.7

        money_price = 0
        token_price = 0
        items_map: dict[str, int] = {}
        catalog = get_catalog()
        for name in keyset:
            amount_min, amount_max = catalog.item_order_amount_limits(name)
            price = catalog.item_price(name)
            token = catalog.item_token_price(name)
            span = max(amount_max - amount_min, 1)
            amount = random.randint(0, span - 1) + amount_min
            money_price += price * amount
            token_price += token * amount
            items_map[name] = amount

        money_price = int(money_price * price_modifier)
        token_price = int(token_price * price_modifier)
        return Order(items_map, money_price, timestamp, token_price)
    except Exception:
        return Order({"wheat": 3}, 0, datetime.now(UTC), 0)


def regenerate(player: Player) -> int:
    if get_orders_amount(player) > len(player.orders):
        player.orders.append(generate_order(player, datetime.now(UTC)))
    return GameErrorCode.OK


def complete_order(player: Player, order_id: int) -> int:
    if order_id < 0 or order_id >= len(player.orders):
        return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES

    order = player.orders[order_id]
    item_booster_percentage = boosters.get_percentage(player.active_boosters.order_items)

    able_to_complete = True
    for item, amount in order.items.items():
        required = round(amount * (1 - item_booster_percentage * 0.01))
        if (player.inventory.get_amount(item) or 0) < required:
            able_to_complete = False

    if order.start_timestamp > datetime.now(UTC):
        able_to_complete = False

    if not able_to_complete:
        return GameErrorCode.ORDER_NOT_ENOUGH_ITEMS_TO_COMPLETE

    for item, amount in order.items.items():
        required = round(amount * (1 - item_booster_percentage * 0.01))
        player.inventory.add_amount(item, -required)

    money_booster_percentage = boosters.get_percentage(player.active_boosters.order_money)
    money_reward = round(order.price * (1 + money_booster_percentage * 0.01))
    token_reward = round(order.token_price * (1 + money_booster_percentage * 0.01))

    order.completed = True
    player.money += money_reward
    player.stats.orders_completed += 1
    player.net_worth += money_reward
    player.wallet.token_balance += token_reward
    player.orders[order_id] = generate_order(
        player, datetime.now(UTC) + timedelta(seconds=settings.orders_regeneration_time_seconds)
    )
    return GameErrorCode.OK


def reroll_order(player: Player, order_id: int) -> int:
    if order_id < 0 or order_id >= len(player.orders):
        return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES

    order = player.orders[order_id]
    if order.start_timestamp >= datetime.now(UTC):
        return GameErrorCode.ORDERS_NOT_READY

    if order.completed:
        return GameErrorCode.ORDER_ALREADY_COMPLETED

    player.orders[order_id] = generate_order(
        player, datetime.now(UTC) + timedelta(seconds=settings.orders_reroll_time_seconds)
    )
    return GameErrorCode.OK
