from datetime import UTC, datetime, timedelta

from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import order_service


def test_get_orders_amount_defaults_to_one_for_non_positive_net_worth() -> None:
    player = Player()
    player.net_worth = 0

    assert order_service.get_orders_amount(player) == 1


def test_get_orders_amount_grows_logarithmically_with_net_worth() -> None:
    player = Player()
    player.net_worth = 25

    assert order_service.get_orders_amount(player) == 3


def test_regenerate_does_not_add_order_when_quota_already_met() -> None:
    player = Player()

    result = order_service.regenerate(player)

    assert result == GameErrorCode.OK
    assert len(player.orders) == 1


def test_regenerate_adds_order_when_quota_allows_more() -> None:
    player = Player()
    player.net_worth = 25

    order_service.regenerate(player)

    assert len(player.orders) == 2


def test_complete_order_rejects_negative_index() -> None:
    player = Player()

    assert order_service.complete_order(player, -1) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_complete_order_rejects_index_beyond_orders() -> None:
    player = Player()

    assert order_service.complete_order(player, 99) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_complete_order_rejects_when_not_enough_items() -> None:
    player = Player()

    result = order_service.complete_order(player, 0)

    assert result == GameErrorCode.ORDER_NOT_ENOUGH_ITEMS_TO_COMPLETE


def test_complete_order_grants_reward_and_replaces_order_on_success() -> None:
    player = Player()
    player.inventory.add_amount("bread", 1)
    money_before = player.money
    original_order = player.orders[0]

    result = order_service.complete_order(player, 0)

    assert result == GameErrorCode.OK
    assert player.money == money_before + 15
    assert player.stats.orders_completed == 1
    assert player.net_worth == 15
    assert player.orders[0] is not original_order


def test_reroll_order_rejects_negative_index() -> None:
    player = Player()

    assert order_service.reroll_order(player, -1) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_reroll_order_rejects_when_not_ready_yet() -> None:
    player = Player()
    player.orders[0].start_timestamp = datetime.now(UTC) + timedelta(seconds=60)

    assert order_service.reroll_order(player, 0) == GameErrorCode.ORDERS_NOT_READY


def test_reroll_order_rejects_completed_order() -> None:
    player = Player()
    player.orders[0].completed = True

    assert order_service.reroll_order(player, 0) == GameErrorCode.ORDER_ALREADY_COMPLETED


def test_reroll_order_replaces_order_on_success() -> None:
    player = Player()
    original_order = player.orders[0]

    result = order_service.reroll_order(player, 0)

    assert result == GameErrorCode.OK
    assert player.orders[0] is not original_order
