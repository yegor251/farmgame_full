from datetime import UTC, datetime, timedelta

from app.domain.bakery import Bakery
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import bakery_service


def test_use_rejects_unknown_work_type() -> None:
    player = Player()
    bakery = Bakery("bakery")

    assert bakery_service.use(bakery, "not-a-work-type", player) == GameErrorCode.SOCKET_WRONG_FORMAT


def test_use_rejects_when_not_enough_items() -> None:
    player = Player()
    bakery = Bakery("bakery")

    assert bakery_service.use(bakery, "bread", player) == GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS


def test_use_rejects_when_all_slots_are_busy() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 10)
    bakery = Bakery("bakery")
    bakery.last_empty_slot = 2

    assert bakery_service.use(bakery, "bread", player) == GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS


def test_use_consumes_items_and_starts_a_slot_on_success() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 10)
    bakery = Bakery("bakery")

    result = bakery_service.use(bakery, "bread", player)

    assert result == GameErrorCode.OK
    assert player.inventory.items["wheat"] == 7
    assert len(bakery.slots) == 1
    assert bakery.slots[0].name == "bread"


def test_collect_rejects_when_no_slots_in_progress() -> None:
    player = Player()
    bakery = Bakery("bakery")

    assert bakery_service.collect(bakery, player) == GameErrorCode.WORK_NOT_STARTED


def test_collect_rejects_when_slot_not_ready() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 10)
    bakery = Bakery("bakery")
    bakery_service.use(bakery, "bread", player)

    assert bakery_service.collect(bakery, player) == GameErrorCode.WORK_NOT_READY


def test_collect_adds_products_and_pops_slot_on_success() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 10)
    bakery = Bakery("bakery")
    bakery_service.use(bakery, "bread", player)
    bakery.slots[0].work_end_timestamp = datetime.now(UTC) - timedelta(seconds=1)

    result = bakery_service.collect(bakery, player)

    assert result == GameErrorCode.OK
    assert player.inventory.items["bread"] == 1
    assert len(bakery.slots) == 0
    assert bakery.last_empty_slot == 0


def test_upgrade_rejects_when_maxed_out() -> None:
    player = Player()
    player.money = 1_000_000
    bakery = Bakery("bakery")
    bakery.curlevel = 6

    assert bakery_service.upgrade(bakery, player) == GameErrorCode.BUILDING_ALREADY_MAXXED_UP


def test_upgrade_rejects_when_not_enough_money() -> None:
    player = Player()
    player.money = 0
    bakery = Bakery("bakery")

    assert bakery_service.upgrade(bakery, player) == GameErrorCode.NOT_ENOUGH_MONEY


def test_upgrade_deducts_price_and_increments_level_on_success() -> None:
    player = Player()
    player.money = 1_000
    bakery = Bakery("bakery")

    result = bakery_service.upgrade(bakery, player)

    assert result == GameErrorCode.OK
    assert bakery.curlevel == 2
    assert player.money == 850


def test_purchase_slot_rejects_when_at_max_purchased_slots() -> None:
    player = Player()
    player.wallet.token_balance = 1_000_000
    bakery = Bakery("bakery")
    bakery.purchased_slots = 3

    assert bakery_service.purchase_slot(bakery, player) == GameErrorCode.BUILDING_ALREADY_MAXXED_UP


def test_purchase_slot_rejects_when_not_enough_tokens() -> None:
    player = Player()
    player.wallet.token_balance = 0
    bakery = Bakery("bakery")

    assert bakery_service.purchase_slot(bakery, player) == GameErrorCode.NOT_ENOUGH_MONEY


def test_purchase_slot_deducts_tokens_and_increments_on_success() -> None:
    player = Player()
    player.wallet.token_balance = 1_000
    bakery = Bakery("bakery")

    result = bakery_service.purchase_slot(bakery, player)

    assert result == GameErrorCode.OK
    assert bakery.purchased_slots == 1
    assert player.wallet.token_balance == 0
