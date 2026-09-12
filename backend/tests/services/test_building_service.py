from app.domain.bakery import Bakery
from app.domain.corral import Corral
from app.domain.garden import Garden
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import building_service


def test_building_exists_reflects_catalog() -> None:
    assert building_service.building_exists("bakery") is True
    assert building_service.building_exists("not-a-building") is False


def test_get_size_returns_multi_tile_dimensions_for_bakery() -> None:
    assert building_service.get_size("bakery") == (3, 2)


def test_get_map_limit_and_price_are_read_from_catalog() -> None:
    assert building_service.get_map_limit("garden") == 999
    assert building_service.get_price("garden") == 10


def test_get_items_by_name_and_level_returns_bakery_work_names_for_level() -> None:
    names = building_service.get_items_by_name_and_level("bakery", 1)

    assert names == {"bread"}


def test_verify_purchase_applies_bakery_price_progression() -> None:
    player = Player()
    player.money = 10_000_000

    player.stats.buildings_placed["bakery"] = 0
    price_first = building_service.get_price("bakery")

    player.stats.buildings_placed["bakery"] = 2
    money_before = player.money
    result = building_service.verify_purchase(player, "bakery")

    assert result == GameErrorCode.OK
    expected_price = int(price_first * 100.0**2)
    assert money_before - player.money == expected_price


def test_verify_purchase_uses_fixed_price_for_bush() -> None:
    player = Player()
    player.money = 10_000

    player.stats.buildings_placed["cherry"] = 5
    money_before = player.money
    result = building_service.verify_purchase(player, "cherry")

    assert result == GameErrorCode.OK
    assert money_before - player.money == building_service.get_price("cherry")


def test_verify_purchase_rejects_when_not_enough_money() -> None:
    player = Player()
    player.money = 0

    result = building_service.verify_purchase(player, "garden")

    assert result == GameErrorCode.NOT_ENOUGH_MONEY
    assert player.money == 0


def test_use_dispatches_by_building_type_and_falls_back_for_unknown() -> None:
    player = Player()
    garden = Garden()

    assert building_service.use(player, garden, "wheat") in (
        GameErrorCode.OK,
        GameErrorCode.NOT_ENOUGH_BUILDING_CONDITIONS,
    )
    assert building_service.use(player, object(), "wheat") == GameErrorCode.SOCKET_WRONG_FORMAT


def test_collect_falls_back_to_wrong_format_for_unsupported_building() -> None:
    player = Player()

    assert building_service.collect(player, object()) == GameErrorCode.SOCKET_WRONG_FORMAT


def test_upgrade_dispatches_only_to_bakery_and_corral() -> None:
    player = Player()
    player.money = 10_000

    corral = Corral("coop")
    bakery = Bakery("bakery")

    assert building_service.upgrade(player, corral) == GameErrorCode.OK
    assert building_service.upgrade(player, bakery) == GameErrorCode.OK
    assert building_service.upgrade(player, Garden()) == GameErrorCode.SOCKET_WRONG_FORMAT


def test_purchase_slot_only_dispatches_to_bakery() -> None:
    player = Player()
    player.wallet.token_balance = 10_000

    assert building_service.purchase_slot(player, Bakery("bakery")) == GameErrorCode.OK
    assert building_service.purchase_slot(player, Corral("coop")) == GameErrorCode.SOCKET_WRONG_FORMAT
