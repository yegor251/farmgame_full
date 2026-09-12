import json
from collections import deque
from datetime import UTC, datetime
from pathlib import Path

from app.domain.bakery import Bakery, Slot
from app.domain.boosters import ActiveBoosters, Booster, BoosterShelfEntry
from app.domain.bush import Bush
from app.domain.client_info import ClientInfo
from app.domain.corral import Corral
from app.domain.deals import Deals
from app.domain.game import Game
from app.domain.garden import Garden
from app.domain.item_container import ItemContainer
from app.domain.obstacle import Obstacle
from app.domain.orders import Order
from app.domain.player import Player
from app.domain.spin import Spin
from app.domain.stats import Stats
from app.domain.transfer_info import Deposit, TransferInfo, Withdraw
from app.domain.wallet import Wallet
from app.domain.world import World
from app.persistence.snapshot_models import (
    ActiveBoostersSnapshot,
    BakerySnapshot,
    BoosterShelfSnapshot,
    BoosterSnapshot,
    BushSnapshot,
    ClientInfoSnapshot,
    CorralSnapshot,
    DealsSnapshot,
    DepositSnapshot,
    GardenSnapshot,
    ItemContainerSnapshot,
    ObstacleSnapshot,
    OrderSnapshot,
    PlacedBuildingSnapshot,
    PlayerInfoSnapshot,
    SlotSnapshot,
    SpinSnapshot,
    StatsSnapshot,
    TransferInfoSnapshot,
    WalletSnapshot,
    WithdrawSnapshot,
    WorldSnapshot,
)
from app.static_data.catalog import get_catalog


def _to_epoch(value: datetime) -> int:
    return int(value.timestamp())


def _from_epoch(value: int) -> datetime:
    return datetime.fromtimestamp(value, tz=UTC)


def _booster_to_snapshot(booster: Booster | None) -> BoosterSnapshot | None:
    if booster is None:
        return None
    return BoosterSnapshot(
        booster_type=booster.booster_type,
        percentage=booster.percentage,
        time=booster.time,
        activate_timestamp=_to_epoch(booster.activate_timestamp),
    )


def _snapshot_to_booster(snapshot: BoosterSnapshot | None) -> Booster | None:
    if snapshot is None:
        return None
    return Booster(
        booster_type=snapshot.booster_type,
        percentage=snapshot.percentage,
        time=snapshot.time,
        activate_timestamp=_from_epoch(snapshot.activate_timestamp),
    )


def _building_to_snapshot(
    building: object,
) -> GardenSnapshot | BakerySnapshot | CorralSnapshot | BushSnapshot | ObstacleSnapshot:
    if isinstance(building, Garden):
        return GardenSnapshot(
            curplant=building.curplant,
            plant_timestamp=_to_epoch(building.plant_timestamp),
            grow_timestamp=_to_epoch(building.grow_timestamp),
        )
    if isinstance(building, Bakery):
        return BakerySnapshot(
            name=building.bakery_type,
            curlevel=building.curlevel,
            slots=[
                SlotSnapshot(
                    name=slot.name,
                    start=_to_epoch(slot.work_start_timestamp),
                    end=_to_epoch(slot.work_end_timestamp),
                )
                for slot in building.slots
            ],
            last_empty_slot=building.last_empty_slot,
            purchased_slots=building.purchased_slots,
            last_end_time=_to_epoch(building.last_end_time),
        )
    if isinstance(building, Corral):
        return CorralSnapshot(
            name=building.corral_type,
            curlevel=building.curlevel,
            work_start=_to_epoch(building.work_start_timestamp) if building.work_start_timestamp else None,
            work_end=_to_epoch(building.work_end_timestamp) if building.work_end_timestamp else None,
            animal_amount=building.animal_amount,
        )
    if isinstance(building, Bush):
        return BushSnapshot(
            name=building.bush_type,
            last_time_collected=_to_epoch(building.last_time_collected),
            ready_timestamp=_to_epoch(building.ready_timestamp),
            collected_amount=building.collected_amount,
        )
    if isinstance(building, Obstacle):
        return ObstacleSnapshot(name=building.obstacle_type)
    raise TypeError(f"Unknown buildable type: {type(building)!r}")


def _snapshot_to_building(snapshot: object) -> Garden | Bakery | Corral | Bush | Obstacle:
    if isinstance(snapshot, GardenSnapshot):
        garden = Garden()
        garden.curplant = snapshot.curplant
        garden.plant_timestamp = _from_epoch(snapshot.plant_timestamp)
        garden.grow_timestamp = _from_epoch(snapshot.grow_timestamp)
        return garden
    if isinstance(snapshot, BakerySnapshot):
        bakery = Bakery(snapshot.name)
        bakery.curlevel = snapshot.curlevel
        bakery.slots = deque(
            Slot(slot.name, _from_epoch(slot.start), _from_epoch(slot.end)) for slot in snapshot.slots
        )
        bakery.last_empty_slot = snapshot.last_empty_slot
        bakery.purchased_slots = snapshot.purchased_slots
        bakery.last_end_time = _from_epoch(snapshot.last_end_time)
        return bakery
    if isinstance(snapshot, CorralSnapshot):
        corral = Corral(snapshot.name)
        corral.curlevel = snapshot.curlevel
        corral.work_start_timestamp = _from_epoch(snapshot.work_start) if snapshot.work_start else None
        corral.work_end_timestamp = _from_epoch(snapshot.work_end) if snapshot.work_end else None
        corral.animal_amount = snapshot.animal_amount
        return corral
    if isinstance(snapshot, BushSnapshot):
        bush = Bush(snapshot.name, get_catalog().bushes[snapshot.name].speed)
        bush.last_time_collected = _from_epoch(snapshot.last_time_collected)
        bush.ready_timestamp = _from_epoch(snapshot.ready_timestamp)
        bush.collected_amount = snapshot.collected_amount
        return bush
    if isinstance(snapshot, ObstacleSnapshot):
        return Obstacle(snapshot.name)
    raise TypeError(f"Unknown buildable snapshot: {type(snapshot)!r}")


class SnapshotStore:
    def __init__(self, sessions_dir: Path) -> None:
        self._sessions_dir = sessions_dir

    def _player_dir(self, tg_id: int) -> Path:
        return self._sessions_dir / str(tg_id) / "player"

    def _game_dir(self, tg_id: int) -> Path:
        return self._sessions_dir / str(tg_id) / "game"

    def _world_dir(self, tg_id: int) -> Path:
        return self._sessions_dir / str(tg_id) / "world"

    def exists(self, tg_id: int) -> bool:
        return (self._player_dir(tg_id) / "info.json").exists()

    def _write(self, path: Path, model: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(model, list):
            payload = json.dumps([item.model_dump(mode="json") for item in model])
        else:
            payload = model.model_dump_json()  # type: ignore[attr-defined]
        path.write_text(payload, encoding="utf-8")

    def save_game(self, game: Game) -> None:
        tg_id = game.client_info.tg_id
        player_dir = self._player_dir(tg_id)

        self._write(
            player_dir / "info.json",
            PlayerInfoSnapshot(money=game.player.money, net_worth=game.player.net_worth),
        )
        self._write(
            player_dir / "inventory.json",
            ItemContainerSnapshot(
                items=game.player.inventory.items,
                items_amount=game.player.inventory.items_amount,
                capacity=game.player.inventory.capacity,
                level=game.player.inventory.level,
            ),
        )
        self._write(
            player_dir / "spin.json",
            SpinSnapshot(
                items=game.player.spin.items,
                drop=game.player.spin.drop,
                activated=game.player.spin.activated,
                generate_timestamp=_to_epoch(game.player.spin.generate_timestamp),
            ),
        )
        self._write(
            player_dir / "orders.json",
            [
                OrderSnapshot(
                    items=order.items,
                    price=order.price,
                    token_price=order.token_price,
                    completed=order.completed,
                    start_timestamp=_to_epoch(order.start_timestamp),
                )
                for order in game.player.orders
            ],
        )
        self._write(
            player_dir / "stats.json",
            StatsSnapshot(
                orders_completed=game.player.stats.orders_completed,
                buildings_placed=game.player.stats.buildings_placed,
            ),
        )
        self._write(
            player_dir / "deals.json",
            DealsSnapshot(
                bought_deals=sorted(game.player.deals.bought_deals),
                token_spent=game.player.deals.token_spent,
                usdt_spent=game.player.deals.usdt_spent,
                ton_spent=game.player.deals.ton_spent,
                boosters=[
                    BoosterShelfSnapshot(
                        booster_type=entry.booster_type, percentage=entry.percentage, time=entry.time
                    )
                    for entry in game.player.deals.boosters
                ],
            ),
        )
        self._write(
            player_dir / "active-boosters.json",
            ActiveBoostersSnapshot(
                order_money=_booster_to_snapshot(game.player.active_boosters.order_money),
                order_items=_booster_to_snapshot(game.player.active_boosters.order_items),
                work_speed=_booster_to_snapshot(game.player.active_boosters.work_speed),
                grow_speed=_booster_to_snapshot(game.player.active_boosters.grow_speed),
            ),
        )
        self._write(
            player_dir / "wallet.json",
            WalletSnapshot(
                token_balance=game.player.wallet.token_balance,
                usdt_balance=game.player.wallet.usdt_balance,
                ton_balance=game.player.wallet.ton_balance,
            ),
        )

        self._write(
            self._game_dir(tg_id) / "transfer-info.json",
            TransferInfoSnapshot(
                deposits=[
                    DepositSnapshot(
                        transaction_id=d.transaction_id,
                        active=d.active,
                        tg_id=d.tg_id,
                        amount=d.amount,
                        time_stamp=d.time_stamp,
                        jetton_signature=d.jetton_signature,
                        commentary=d.commentary,
                    )
                    for d in game.transfer_info.deposits
                ],
                withdraws=[
                    WithdrawSnapshot(
                        transaction_id=w.transaction_id,
                        status=w.status,
                        tg_id=w.tg_id,
                        wallet=w.wallet,
                        amount=w.amount,
                        time_stamp=w.time_stamp,
                    )
                    for w in game.transfer_info.withdraws
                ],
            ),
        )
        self._write(
            self._game_dir(tg_id) / "client-info.json",
            ClientInfoSnapshot(
                tg_id=game.client_info.tg_id,
                ref_id=game.client_info.ref_id,
                wallet=game.client_info.wallet,
                banned=game.client_info.banned,
                strikes=game.client_info.strikes,
                referrals=game.client_info.referrals,
            ),
        )

        placed: list[PlacedBuildingSnapshot] = []
        for x, column in enumerate(game.world.tile_array):
            for y, tile in enumerate(column):
                if tile.place is not None:
                    placed.append(
                        PlacedBuildingSnapshot(x=x, y=y, building=_building_to_snapshot(tile.place))
                    )
        self._write(self._world_dir(tg_id) / "world.json", WorldSnapshot(buildings=placed))

    def load_game(self, tg_id: int) -> Game:
        player_dir = self._player_dir(tg_id)
        game_dir = self._game_dir(tg_id)
        world_dir = self._world_dir(tg_id)
        catalog = get_catalog()

        info = PlayerInfoSnapshot.model_validate_json((player_dir / "info.json").read_text())
        inventory_snap = ItemContainerSnapshot.model_validate_json(
            (player_dir / "inventory.json").read_text()
        )
        spin_snap = SpinSnapshot.model_validate_json((player_dir / "spin.json").read_text())
        orders_snap = [
            OrderSnapshot.model_validate(item)
            for item in json.loads((player_dir / "orders.json").read_text())
        ]
        stats_snap = StatsSnapshot.model_validate_json((player_dir / "stats.json").read_text())
        deals_snap = DealsSnapshot.model_validate_json((player_dir / "deals.json").read_text())
        active_boosters_snap = ActiveBoostersSnapshot.model_validate_json(
            (player_dir / "active-boosters.json").read_text()
        )
        wallet_snap = WalletSnapshot.model_validate_json((player_dir / "wallet.json").read_text())
        transfer_snap = TransferInfoSnapshot.model_validate_json(
            (game_dir / "transfer-info.json").read_text()
        )
        client_snap = ClientInfoSnapshot.model_validate_json((game_dir / "client-info.json").read_text())
        world_snap = WorldSnapshot.model_validate_json((world_dir / "world.json").read_text())

        game = Game.__new__(Game)
        player = Player.__new__(Player)

        inventory = ItemContainer()
        inventory.items = {
            name: amount
            for name, amount in inventory_snap.items.items()
            if name in catalog.items or name in catalog.plants
        }
        inventory.items_amount = inventory_snap.items_amount
        inventory.capacity = inventory_snap.capacity
        inventory.level = inventory_snap.level
        player.inventory = inventory

        player.money = info.money
        player.net_worth = info.net_worth
        player.spin = Spin(spin_snap.items, spin_snap.drop)
        player.spin.activated = spin_snap.activated
        player.spin.generate_timestamp = _from_epoch(spin_snap.generate_timestamp)
        player.orders = [
            Order(order.items, order.price, _from_epoch(order.start_timestamp), order.token_price)
            for order in orders_snap
        ]
        for order, snap in zip(player.orders, orders_snap, strict=True):
            order.completed = snap.completed

        stats = Stats([])
        stats.orders_completed = stats_snap.orders_completed
        stats.buildings_placed = stats_snap.buildings_placed
        player.stats = stats

        deals = Deals()
        deals.bought_deals = set(deals_snap.bought_deals)
        deals.token_spent = deals_snap.token_spent
        deals.usdt_spent = deals_snap.usdt_spent
        deals.ton_spent = deals_snap.ton_spent
        deals.boosters = [
            BoosterShelfEntry(entry.booster_type, entry.percentage, entry.time)
            for entry in deals_snap.boosters
        ]
        player.deals = deals

        active_boosters = ActiveBoosters()
        active_boosters.order_money = _snapshot_to_booster(active_boosters_snap.order_money)
        active_boosters.order_items = _snapshot_to_booster(active_boosters_snap.order_items)
        active_boosters.work_speed = _snapshot_to_booster(active_boosters_snap.work_speed)
        active_boosters.grow_speed = _snapshot_to_booster(active_boosters_snap.grow_speed)
        player.active_boosters = active_boosters

        wallet = Wallet()
        wallet.token_balance = wallet_snap.token_balance
        wallet.usdt_balance = wallet_snap.usdt_balance
        wallet.ton_balance = wallet_snap.ton_balance
        player.wallet = wallet

        game.player = player

        world = World()
        for placed in world_snap.buildings:
            building = _snapshot_to_building(placed.building)
            if isinstance(building, Garden):
                size = (1, 1)
            elif isinstance(building, Obstacle):
                obstacle_info = catalog.obstacles[building.get_name()]
                size = (obstacle_info.sizex, obstacle_info.sizey)
            else:
                size = catalog.building_size(building.get_name())
            world.place_existing(building, placed.x, placed.y, size)
        game.world = world

        transfer_info = TransferInfo(
            deposits=[
                Deposit(
                    transaction_id=d.transaction_id,
                    active=d.active,
                    tg_id=d.tg_id,
                    amount=d.amount,
                    time_stamp=d.time_stamp,
                    jetton_signature=d.jetton_signature,
                    commentary=d.commentary,
                )
                for d in transfer_snap.deposits
            ],
            withdraws=[
                Withdraw(
                    transaction_id=w.transaction_id,
                    status=w.status,
                    tg_id=w.tg_id,
                    wallet=w.wallet,
                    amount=w.amount,
                    time_stamp=w.time_stamp,
                )
                for w in transfer_snap.withdraws
            ],
        )
        game.transfer_info = transfer_info

        client_info = ClientInfo(client_snap.tg_id, client_snap.ref_id)
        client_info.wallet = client_snap.wallet
        client_info.banned = client_snap.banned
        client_info.strikes = client_snap.strikes
        client_info.referrals = client_snap.referrals
        game.client_info = client_info

        game.last_operation = 0
        return game
