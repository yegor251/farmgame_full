from app.api_models.boosters import (
    ActiveBoosterResponse,
    ActiveBoostersResponse,
    BoosterShelfResponse,
)
from app.api_models.deal import DealResponse, RewardResponse
from app.api_models.game_session import GameSessionResponse, OperationResponse
from app.api_models.item_container import ItemsContainerResponse
from app.api_models.order import OrderResponse
from app.api_models.player import PlayerResponse
from app.api_models.spin import SlotResponse, SpinResponse
from app.api_models.transaction import DepositResponse, WithdrawResponse
from app.api_models.wallet import WalletResponse
from app.api_models.world import BuildingResponse, BuildingSlotResponse, WorldResponse
from app.domain.bakery import Bakery
from app.domain.boosters import ActiveBoosters, Booster
from app.domain.bush import Bush
from app.domain.corral import Corral
from app.domain.game import Game
from app.domain.garden import Garden
from app.domain.obstacle import Obstacle
from app.domain.player import Player
from app.domain.tile import Tile
from app.domain.world import World
from app.errors import GameErrorCode
from app.static_data.catalog import get_catalog


def _epoch(value: object) -> int:
    return int(value.timestamp())  # type: ignore[attr-defined]


def _active_booster(booster: Booster | None) -> ActiveBoosterResponse | None:
    if booster is None:
        return None
    return ActiveBoosterResponse(
        percentage=booster.percentage,
        time=booster.time,
        activate_time_stamp=_epoch(booster.activate_timestamp),
    )


def build_active_boosters(active_boosters: ActiveBoosters) -> ActiveBoostersResponse:
    return ActiveBoostersResponse(
        order_money=_active_booster(active_boosters.order_money),
        order_items=_active_booster(active_boosters.order_items),
        work_speed=_active_booster(active_boosters.work_speed),
        grow_speed=_active_booster(active_boosters.grow_speed),
    )


def build_player(player: Player) -> PlayerResponse:
    spin_response = SpinResponse(
        items=[SlotResponse(item=item, amount=amount) for item, amount in player.spin.items],
        drop=SlotResponse(item=player.spin.drop[0], amount=player.spin.drop[1]),
        generate_time_stamp=_epoch(player.spin.generate_timestamp),
        activated=player.spin.activated,
    )
    orders_response = [
        OrderResponse(
            order_items=order.items,
            order_price=order.price,
            order_token_price=order.token_price,
            completed=order.completed,
            time_stamp=_epoch(order.start_timestamp),
        )
        for order in player.orders
    ]
    return PlayerResponse(
        money=player.money,
        networth=player.net_worth,
        inventory=ItemsContainerResponse(map=player.inventory.items, level=player.inventory.level),
        spin=spin_response,
        orders=orders_response,
    )


def build_wallet(player: Player) -> WalletResponse:
    return WalletResponse(
        usdt_balance=player.wallet.usdt_balance,
        ton_balance=player.wallet.ton_balance,
        token_balance=player.wallet.token_balance,
    )


def _building_from_tile(tile: Tile, x: int, y: int) -> BuildingResponse | None:
    building = tile.place
    if building is None:
        return None

    if isinstance(building, Garden):
        plant = building.curplant if building.curplant is not None else "none"
        return BuildingResponse(
            name="garden",
            x=x,
            y=y,
            slots=[
                BuildingSlotResponse(
                    work_name=plant,
                    work_start_time_stamp=_epoch(building.plant_timestamp),
                    work_end_time_stamp=_epoch(building.grow_timestamp),
                )
            ],
        )
    if isinstance(building, Bakery):
        slots = [
            BuildingSlotResponse(
                work_name=slot.name,
                work_start_time_stamp=_epoch(slot.work_start_timestamp),
                work_end_time_stamp=_epoch(slot.work_end_timestamp),
            )
            for slot in building.slots
        ]
        return BuildingResponse(
            name=building.get_name(),
            x=x,
            y=y,
            slots=slots,
            integer_data=building.purchased_slots,
            level=building.curlevel,
        )
    if isinstance(building, Corral):
        slots = []
        if building.work_start_timestamp is not None:
            assert building.work_end_timestamp is not None
            slots.append(
                BuildingSlotResponse(
                    work_name=None,
                    work_start_time_stamp=_epoch(building.work_start_timestamp),
                    work_end_time_stamp=_epoch(building.work_end_timestamp),
                )
            )
        return BuildingResponse(
            name=building.get_name(),
            x=x,
            y=y,
            slots=slots,
            integer_data=building.animal_amount,
            level=building.curlevel,
        )
    if isinstance(building, Bush):
        slots = [
            BuildingSlotResponse(
                work_name=None,
                work_start_time_stamp=_epoch(building.last_time_collected),
                work_end_time_stamp=_epoch(building.ready_timestamp),
            )
        ]
        return BuildingResponse(
            name=building.get_name(),
            x=x,
            y=y,
            slots=slots,
            integer_data=building.collected_amount,
        )
    if isinstance(building, Obstacle):
        return BuildingResponse(name=building.get_name(), x=x, y=y, slots=[])
    return None


def build_world(world: World) -> WorldResponse:
    buildings: list[BuildingResponse] = []
    for x, column in enumerate(world.tile_array):
        for y, tile in enumerate(column):
            response = _building_from_tile(tile, x, y)
            if response is not None:
                buildings.append(response)
    return WorldResponse(tile_array=buildings)


def build_deposits(game: Game) -> list[DepositResponse]:
    return [
        DepositResponse(
            transaction_id=d.transaction_id,
            active=d.active,
            tg_id=d.tg_id,
            amount=d.amount,
            time_stamp=d.time_stamp,
            jetton_signature=d.jetton_signature,
            commentary=d.commentary,
        )
        for d in game.transfer_info.deposits
    ]


def build_withdraws(game: Game) -> list[WithdrawResponse]:
    return [
        WithdrawResponse(
            transaction_id=w.transaction_id,
            status=w.status,
            tg_id=w.tg_id,
            wallet=w.wallet,
            amount=w.amount,
            time_stamp=w.time_stamp,
        )
        for w in game.transfer_info.withdraws
    ]


def build_available_deals(game: Game) -> dict[str, DealResponse]:
    catalog = get_catalog()
    return {
        name: DealResponse(
            name=deal.name,
            ton_price=deal.ton_price,
            token_price=deal.token_price,
            usdt_price=deal.usdt_price,
            reward=RewardResponse(
                money=deal.reward.money,
                token=deal.reward.token,
                boosters=(
                    [
                        BoosterShelfResponse(
                            booster_type=booster.booster_type,
                            percentage=booster.percentage,
                            time=booster.time,
                        )
                        for booster in deal.reward.boosters
                    ]
                    if deal.reward.boosters is not None
                    else None
                ),
            ),
        )
        for name, deal in catalog.deals.items()
        if name not in game.player.deals.bought_deals
    }


def build_available_boosters(game: Game) -> list[BoosterShelfResponse]:
    return [
        BoosterShelfResponse(booster_type=entry.booster_type, percentage=entry.percentage, time=entry.time)
        for entry in game.player.deals.boosters
    ]


def build_game_session(game: Game) -> GameSessionResponse:
    return GameSessionResponse(
        data_type="game-session",
        player=build_player(game.player),
        world=build_world(game.world),
        deposits=build_deposits(game),
        withdraws=build_withdraws(game),
        wallet=build_wallet(game.player),
        available_deals=build_available_deals(game),
        available_boosters=build_available_boosters(game),
        active_boosters=build_active_boosters(game.player.active_boosters),
        businesses=[],
        ref_amount=len(game.client_info.referrals),
    )


def build_game_session_regen(game: Game) -> GameSessionResponse:
    return GameSessionResponse(
        data_type="game-session-regen",
        player=build_player(game.player),
        world=None,
        deposits=None,
        withdraws=None,
        wallet=build_wallet(game.player),
        available_deals=None,
        available_boosters=build_available_boosters(game),
        active_boosters=build_active_boosters(game.player.active_boosters),
        businesses=[],
        ref_amount=len(game.client_info.referrals),
    )


def build_operation_response(code: int) -> OperationResponse:
    return OperationResponse(code=code)


def build_state_response(game: Game) -> GameSessionResponse | OperationResponse:
    if game.last_operation == GameErrorCode.CONNECTED:
        return build_game_session(game)
    if game.last_operation == GameErrorCode.REGENERATION:
        return build_game_session_regen(game)
    return build_operation_response(game.last_operation)
