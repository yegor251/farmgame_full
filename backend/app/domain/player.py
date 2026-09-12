from datetime import UTC, datetime

from app.domain.boosters import ActiveBoosters
from app.domain.deals import Deals
from app.domain.item_container import ItemContainer
from app.domain.orders import Order
from app.domain.spin import Spin
from app.domain.stats import Stats
from app.domain.wallet import Wallet
from app.static_data.catalog import get_catalog


class Player:
    def __init__(self) -> None:
        self.inventory = ItemContainer()
        self.money = 20
        self.net_worth = 0
        self.spin = Spin(
            [("money", 10), ("bread", 1), ("wheat", 1), ("wheat", 2), ("wheat", 3), ("wheat", 4)],
            ("wheat", 2),
        )
        self.orders: list[Order] = [Order({"bread": 1}, 15, datetime.now(UTC), 0)]
        self.stats = Stats(list(get_catalog().building_type_by_name.keys()))
        self.deals = Deals()
        self.active_boosters = ActiveBoosters()
        self.wallet = Wallet()
