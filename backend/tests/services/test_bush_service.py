from datetime import UTC, datetime, timedelta

from app.domain.bush import Bush
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import bush_service


def test_use_rejects_when_product_limit_not_reached() -> None:
    player = Player()
    bush = Bush("cherry", speed_seconds=46800)

    assert bush_service.use(bush, player, "sell") == GameErrorCode.BUSH_NOT_EXPIRED


def test_use_rejects_when_not_enough_money() -> None:
    player = Player()
    player.money = 0
    bush = Bush("cherry", speed_seconds=46800)
    bush.collected_amount = 3

    assert bush_service.use(bush, player, "sell") == GameErrorCode.NOT_ENOUGH_MONEY


def test_use_resets_bush_and_charges_player_on_success() -> None:
    player = Player()
    player.money = 10_000
    money_before = player.money
    bush = Bush("cherry", speed_seconds=46800)
    bush.collected_amount = 3

    result = bush_service.use(bush, player, "sell")

    assert result == GameErrorCode.OK
    assert bush.collected_amount == 0
    assert money_before - player.money == round(410 * 1.5)


def test_collect_rejects_when_not_ready() -> None:
    player = Player()
    bush = Bush("cherry", speed_seconds=46800)

    assert bush_service.collect(bush, player) == GameErrorCode.WORK_NOT_READY


def test_collect_rejects_when_product_limit_reached() -> None:
    player = Player()
    bush = Bush("cherry", speed_seconds=1)
    bush.collected_amount = 3
    bush.ready_timestamp = datetime.now(UTC) - timedelta(seconds=1)

    assert bush_service.collect(bush, player) == GameErrorCode.BUSH_EXPIRED


def test_collect_adds_products_and_reschedules_on_success() -> None:
    player = Player()
    bush = Bush("cherry", speed_seconds=46800)
    bush.ready_timestamp = datetime.now(UTC) - timedelta(seconds=1)

    result = bush_service.collect(bush, player)

    assert result == GameErrorCode.OK
    assert player.inventory.items["cherry"] == 3
    assert bush.ready_timestamp > datetime.now(UTC)
