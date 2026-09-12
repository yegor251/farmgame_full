from datetime import UTC, datetime, timedelta

from app.domain.corral import Corral
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import corral_service


def test_buy_animal_rejects_at_max_capacity() -> None:
    player = Player()
    corral = Corral("coop")
    corral.animal_amount = 8

    assert corral_service.buy_animal(corral, player) == GameErrorCode.CORRAL_ALREADY_MAX_ANIMALS


def test_buy_animal_rejects_when_not_enough_money() -> None:
    player = Player()
    player.money = 0
    corral = Corral("coop")

    assert corral_service.buy_animal(corral, player) == GameErrorCode.NOT_ENOUGH_MONEY


def test_buy_animal_charges_player_and_increments_amount() -> None:
    player = Player()
    player.money = 1000
    corral = Corral("coop")

    result = corral_service.buy_animal(corral, player)

    assert result == GameErrorCode.OK
    assert corral.animal_amount == 1
    assert player.money == 920


def test_start_work_rejects_when_already_working() -> None:
    player = Player()
    corral = Corral("coop")
    corral.start_work(600)

    assert corral_service.start_work(corral, player) == GameErrorCode.WORK_NOT_READY


def test_start_work_rejects_when_not_enough_feed() -> None:
    player = Player()
    corral = Corral("coop")
    corral.animal_amount = 1

    assert corral_service.start_work(corral, player) == GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS


def test_start_work_consumes_feed_and_schedules_completion() -> None:
    player = Player()
    player.inventory.add_amount("chickenFeed", 5)
    corral = Corral("coop")
    corral.animal_amount = 1

    result = corral_service.start_work(corral, player)

    assert result == GameErrorCode.OK
    assert player.inventory.items["chickenFeed"] == 4
    assert corral.work_end_timestamp is not None


def test_use_dispatches_buy_and_start_and_rejects_unknown() -> None:
    player = Player()
    player.money = 1000
    corral = Corral("coop")

    assert corral_service.use(corral, player, "buy") == GameErrorCode.OK
    assert corral_service.use(corral, player, "unknown") == GameErrorCode.SOCKET_WRONG_FORMAT


def test_collect_rejects_when_work_not_started() -> None:
    player = Player()
    corral = Corral("coop")

    assert corral_service.collect(corral, player) == GameErrorCode.WORK_NOT_STARTED


def test_collect_rejects_when_not_ready() -> None:
    player = Player()
    corral = Corral("coop")
    corral.start_work(600)

    assert corral_service.collect(corral, player) == GameErrorCode.WORK_NOT_READY


def test_collect_adds_products_and_resets_on_success() -> None:
    player = Player()
    corral = Corral("coop")
    corral.animal_amount = 1
    corral.start_work(600)
    corral.work_end_timestamp = datetime.now(UTC) - timedelta(seconds=1)

    result = corral_service.collect(corral, player)

    assert result == GameErrorCode.OK
    assert player.inventory.items["egg"] == 1
    assert corral.work_start_timestamp is None


def test_upgrade_rejects_when_maxed_out() -> None:
    player = Player()
    player.money = 1_000_000
    corral = Corral("coop")
    corral.curlevel = 4

    assert corral_service.upgrade(corral, player) == GameErrorCode.BUILDING_ALREADY_MAXXED_UP


def test_upgrade_rejects_when_not_enough_money() -> None:
    player = Player()
    player.money = 0
    corral = Corral("coop")

    assert corral_service.upgrade(corral, player) == GameErrorCode.NOT_ENOUGH_MONEY


def test_upgrade_increments_level_without_deducting_money() -> None:
    player = Player()
    player.money = 1_000_000
    money_before = player.money
    corral = Corral("coop")

    result = corral_service.upgrade(corral, player)

    assert result == GameErrorCode.OK
    assert corral.curlevel == 2
    assert player.money == money_before
