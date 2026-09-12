from app.domain.player import Player
from app.static_data.catalog import get_catalog


def test_new_player_has_starting_money_and_empty_inventory() -> None:
    player = Player()

    assert player.money == 20
    assert player.net_worth == 0
    assert player.inventory.items == {}


def test_new_player_has_starting_spin_configuration() -> None:
    player = Player()

    assert player.spin.drop == ("wheat", 2)
    assert ("money", 10) in player.spin.items
    assert player.spin.activated is False


def test_new_player_has_one_starting_bread_order() -> None:
    player = Player()

    assert len(player.orders) == 1
    assert player.orders[0].items == {"bread": 1}
    assert player.orders[0].completed is False


def test_new_player_stats_track_every_known_building() -> None:
    player = Player()

    assert set(player.stats.buildings_placed.keys()) == set(get_catalog().building_type_by_name.keys())
    assert all(count == 0 for count in player.stats.buildings_placed.values())


def test_new_player_has_no_bought_deals_or_active_boosters() -> None:
    player = Player()

    assert player.deals.bought_deals == set()
    assert player.active_boosters.get("WorkSpeed") is None
    assert player.wallet.token_balance == 0
