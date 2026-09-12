from datetime import UTC, datetime

from app.domain.boosters import Booster
from app.domain.game import Game
from app.domain.obstacle import Obstacle
from app.domain.transfer_info import Deposit, Withdraw
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


class _FakeDepositRepository:
    async def get_deposits_by_user_id(self, tg_id: int) -> list[Deposit]:
        return []

    async def close_deposit_by_transaction_id(self, transaction_id: int) -> bool:
        return True


class _FakeWithdrawRepository:
    async def check_withdraw_by_info(self, transaction_id: int) -> Withdraw | None:
        return None

    async def register_withdraw(self, withdraw: Withdraw) -> bool:
        return True


def test_first_init_seeds_starting_wheat_and_map_obstacles() -> None:
    game = Game(tg_id=1, ref_id=0)

    game.first_init()

    assert game.player.inventory.items["wheat"] == 4
    start_build = get_catalog().map.map[0]
    building = game.world.get_building(start_build.x, start_build.y)
    assert isinstance(building, Obstacle)
    assert building.get_name() == start_build.name


def test_on_ban_and_on_unban_toggle_banned_flag() -> None:
    game = Game(tg_id=1, ref_id=0)

    game.on_ban()
    assert game.client_info.banned is True

    game.on_unban()
    assert game.client_info.banned is False


async def test_on_connect_regenerates_and_marks_connected() -> None:
    game = Game(tg_id=1, ref_id=0)

    await game.on_connect(_FakeDepositRepository(), _FakeWithdrawRepository())

    assert game.last_operation == GameErrorCode.CONNECTED


def test_on_place_succeeds_and_deducts_price_and_increments_stats() -> None:
    game = Game(tg_id=1, ref_id=0)

    game.on_place("garden", 5, 5)

    assert game.last_operation == GameErrorCode.OK
    assert game.player.money == 10
    assert game.player.stats.buildings_placed["garden"] == 1
    assert game.world.get_building(5, 5) is not None


def test_on_place_fails_when_map_limit_reached_and_does_not_touch_world() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.stats.buildings_placed["garden"] = get_catalog().building_map_limit("garden")

    game.on_place("garden", 5, 5)

    assert game.last_operation == GameErrorCode.BUILDING_LIMIT_EXCEEDED
    assert game.world.get_building(5, 5) is None


def test_on_place_fails_when_tile_occupied_and_stats_unchanged() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.world.place_new("garden", 5, 5, (1, 1))

    game.on_place("garden", 5, 5)

    assert game.last_operation == GameErrorCode.NOT_ABLE_TO_PLACE
    assert game.player.stats.buildings_placed["garden"] == 0


def test_on_place_fails_when_not_enough_money_and_tile_stays_free() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.money = 0

    game.on_place("garden", 5, 5)

    assert game.last_operation == GameErrorCode.NOT_ENOUGH_MONEY
    assert game.world.get_building(5, 5) is None
    assert game.player.stats.buildings_placed["garden"] == 0


def test_on_use_on_empty_tile_reports_building_not_placed() -> None:
    game = Game(tg_id=1, ref_id=0)

    game.on_use("wheat", 5, 5)

    assert game.last_operation == GameErrorCode.BUILDING_NOT_PLACED


def test_on_purchase_deal_short_circuits_when_already_bought() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.player.deals.bought_deals.add("starter")

    game.on_purchase_deal("starter")

    assert game.last_operation == GameErrorCode.DEAL_HAS_BEEN_ALREADY_BOUGHT


def test_on_activate_booster_requeues_world_even_when_activation_fails() -> None:
    game = Game(tg_id=1, ref_id=0)
    game.on_place("garden", 5, 5)
    building = game.world.get_building(5, 5)
    assert building is not None
    building.plant("wheat", 1000, booster_percentage=0)  # type: ignore[attr-defined]
    grow_timestamp_before = building.grow_timestamp  # type: ignore[attr-defined]
    game.player.active_boosters.work_speed = Booster(
        booster_type="WorkSpeed", percentage=50, time=200, activate_timestamp=datetime.now(UTC)
    )

    game.on_activate_booster(0)

    assert game.last_operation == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES
    assert building.grow_timestamp < grow_timestamp_before  # type: ignore[attr-defined]
