from datetime import UTC, datetime
from pathlib import Path

from app.domain.boosters import Booster, BoosterShelfEntry
from app.domain.game import Game
from app.domain.garden import Garden
from app.domain.obstacle import Obstacle
from app.errors import GameErrorCode
from app.persistence.snapshot_store import SnapshotStore
from app.services.obstacle_service import place_obstacle_unsafe
from app.static_data.catalog import get_catalog


def test_exists_is_false_before_save_and_true_after_save(tmp_path: Path) -> None:
    store = SnapshotStore(tmp_path)
    game = Game(555, 0)

    assert store.exists(555) is False

    store.save_game(game)

    assert store.exists(555) is True


def test_round_trip_preserves_player_state(tmp_path: Path) -> None:
    store = SnapshotStore(tmp_path)
    game = Game(777, 3)
    game.player.money = 12345
    game.player.net_worth = 42
    game.player.inventory.add_amount("wheat", 6)
    game.player.wallet.token_balance = 500
    game.player.wallet.usdt_balance = 10
    game.player.wallet.ton_balance = 20
    game.player.stats.buildings_placed["garden"] = 2
    game.player.stats.orders_completed = 5
    game.player.deals.bought_deals.add("starter")
    game.player.deals.token_spent = 100
    game.player.deals.boosters.append(BoosterShelfEntry(booster_type="WorkSpeed", percentage=20, time=3600))
    game.player.active_boosters.grow_speed = Booster(
        booster_type="GrowSpeed", percentage=15, time=1800, activate_timestamp=datetime.now(UTC)
    )
    game.client_info.strikes = 2
    game.client_info.referrals = [1, 2, 3]

    store.save_game(game)
    loaded = store.load_game(777)

    assert loaded.player.money == 12345
    assert loaded.player.net_worth == 42
    assert loaded.player.inventory.items["wheat"] == 6
    assert loaded.player.wallet.token_balance == 500
    assert loaded.player.wallet.usdt_balance == 10
    assert loaded.player.wallet.ton_balance == 20
    assert loaded.player.stats.buildings_placed["garden"] == 2
    assert loaded.player.stats.orders_completed == 5
    assert loaded.player.deals.bought_deals == {"starter"}
    assert loaded.player.deals.token_spent == 100
    assert loaded.player.deals.boosters[0].booster_type == "WorkSpeed"
    assert loaded.player.active_boosters.grow_speed is not None
    assert loaded.player.active_boosters.grow_speed.percentage == 15
    assert loaded.player.active_boosters.order_money is None
    assert loaded.client_info.strikes == 2
    assert loaded.client_info.referrals == [1, 2, 3]


def test_round_trip_preserves_starting_order() -> None:
    game = Game(888, 0)
    original_order = game.player.orders[0]

    assert original_order.items == {"bread": 1}
    assert original_order.price == 15
    assert original_order.completed is False


def test_round_trip_preserves_orders(tmp_path: Path) -> None:
    store = SnapshotStore(tmp_path)
    game = Game(888, 0)
    game.player.orders[0].completed = True

    store.save_game(game)
    loaded = store.load_game(888)

    assert len(loaded.player.orders) == 1
    assert loaded.player.orders[0].items == {"bread": 1}
    assert loaded.player.orders[0].price == 15
    assert loaded.player.orders[0].completed is True


def test_load_filters_out_items_no_longer_in_the_static_catalog(tmp_path: Path) -> None:
    store = SnapshotStore(tmp_path)
    game = Game(999, 0)
    game.player.inventory.items["totally-illegal-item"] = 5
    game.player.inventory.items_amount += 5
    game.player.inventory.add_amount("wheat", 1)

    store.save_game(game)
    loaded = store.load_game(999)

    assert "totally-illegal-item" not in loaded.player.inventory.items
    assert loaded.player.inventory.items["wheat"] == 1


def test_round_trip_preserves_placed_garden_and_obstacle(tmp_path: Path) -> None:
    store = SnapshotStore(tmp_path)
    game = Game(1000, 0)

    assert game.world.place_new("garden", 0, 0, (1, 1)) == GameErrorCode.OK
    garden = game.world.get_building(0, 0)
    assert isinstance(garden, Garden)
    garden.plant("wheat", 60, 0)

    obstacle_name = next(iter(get_catalog().obstacles))
    place_obstacle_unsafe(game, 5, 5, obstacle_name)

    store.save_game(game)
    loaded = store.load_game(1000)

    loaded_garden = loaded.world.get_building(0, 0)
    assert isinstance(loaded_garden, Garden)
    assert loaded_garden.curplant == "wheat"

    loaded_obstacle = loaded.world.get_building(5, 5)
    assert isinstance(loaded_obstacle, Obstacle)
    assert loaded_obstacle.obstacle_type == obstacle_name
