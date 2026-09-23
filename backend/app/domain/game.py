from app.domain import boosters
from app.domain.client_info import ClientInfo
from app.domain.player import Player
from app.domain.transfer_info import TransferInfo
from app.domain.world import World
from app.errors import GameErrorCode
from app.persistence.contracts import DepositRepository
from app.services import (
    ambar_service,
    booster_service,
    building_service,
    deposit_service,
    obstacle_service,
    order_service,
    shop_service,
    spin_service,
)
from app.static_data.catalog import get_catalog


class Game:
    def __init__(self, tg_id: int, ref_id: int) -> None:
        self.player = Player()
        self.world = World()
        self.transfer_info = TransferInfo()
        self.client_info = ClientInfo(tg_id, ref_id)
        self.last_operation: int = 0

    def first_init(self) -> None:
        self.player.inventory.add_amount("wheat", 4)
        for start_build in get_catalog().map.map:
            obstacle_service.place_obstacle_unsafe(self, start_build.x, start_build.y, start_build.name)

    def on_ban(self) -> None:
        self.client_info.banned = True

    def on_unban(self) -> None:
        self.client_info.banned = False

    async def on_connect(self, deposit_repository: DepositRepository) -> None:
        self.on_regenerate()
        await deposit_service.check(self, deposit_repository)
        self.last_operation = GameErrorCode.CONNECTED

    def on_use(self, item: str, x: int, y: int) -> None:
        if self.world.validate_use(x, y) == GameErrorCode.OK:
            building = self.world.get_building(x, y)
            self.last_operation = building_service.use(self.player, building, item)
        else:
            self.last_operation = GameErrorCode.BUILDING_NOT_PLACED

    def on_collect(self, x: int, y: int) -> None:
        if self.world.validate_use(x, y) == GameErrorCode.OK:
            building = self.world.get_building(x, y)
            self.last_operation = building_service.collect(self.player, building)
        else:
            self.last_operation = GameErrorCode.BUILDING_NOT_PLACED

    def on_buy(self, item: str, amount: int) -> None:
        self.last_operation = shop_service.buy(item, amount, self.player)

    def on_place(self, building: str, x: int, y: int) -> None:
        catalog = get_catalog()
        if self.player.stats.buildings_placed[building] >= catalog.building_map_limit(building):
            self.last_operation = GameErrorCode.BUILDING_LIMIT_EXCEEDED
            return

        size = catalog.building_size(building)
        if self.world.validate_place(x, y, size) != GameErrorCode.OK:
            self.last_operation = GameErrorCode.NOT_ABLE_TO_PLACE
            return

        if building_service.verify_purchase(self.player, building) != GameErrorCode.OK:
            self.last_operation = GameErrorCode.NOT_ENOUGH_MONEY
            return

        self.last_operation = self.world.place_new(building, x, y, size)
        if self.last_operation == GameErrorCode.OK:
            self.player.stats.buildings_placed[building] += 1

    def on_move(self, x: int, y: int, to_x: int, to_y: int) -> None:
        self.last_operation = self.world.move_building(x, y, to_x, to_y)

    def on_regenerate(self) -> None:
        spin_service.regenerate(self.player)
        order_service.regenerate(self.player)
        boosters.regenerate(self.player.active_boosters)
        self.last_operation = GameErrorCode.REGENERATION

    def on_spin(self) -> None:
        self.last_operation = spin_service.spin_wheel(self.player)

    def on_complete_order(self, order_id: int) -> None:
        self.last_operation = order_service.complete_order(self.player, order_id)

    def on_reroll_order(self, order_id: int) -> None:
        self.last_operation = order_service.reroll_order(self.player, order_id)

    def on_upgrade(self, x: int, y: int) -> None:
        if self.world.validate_use(x, y) == GameErrorCode.OK:
            building = self.world.get_building(x, y)
            self.last_operation = building_service.upgrade(self.player, building)
        else:
            self.last_operation = GameErrorCode.BUILDING_NOT_PLACED

    def on_claim_deposit(self, deposit_id: int) -> None:
        self.last_operation = deposit_service.claim(self, deposit_id)

    def on_purchase_slot(self, x: int, y: int) -> None:
        if self.world.validate_use(x, y) == GameErrorCode.OK:
            building = self.world.get_building(x, y)
            self.last_operation = building_service.purchase_slot(self.player, building)
        else:
            self.last_operation = GameErrorCode.BUILDING_NOT_PLACED

    def on_purchase_deal(self, deal_name: str) -> None:
        if deal_name not in self.player.deals.bought_deals:
            self.last_operation = shop_service.purchase_deal(self.player, deal_name)
        else:
            self.last_operation = GameErrorCode.DEAL_HAS_BEEN_ALREADY_BOUGHT

    def on_activate_booster(self, booster_id: int) -> None:
        self.last_operation = booster_service.activate_by_index(self.player, booster_id)
        self.world.requeue_all(self.player)

    def on_inventory_upgrade(self) -> None:
        self.last_operation = ambar_service.upgrade_inventory(self.player)

    def on_remove_obstacle(self, x: int, y: int) -> None:
        self.last_operation = obstacle_service.remove_obstacle(self, x, y)
