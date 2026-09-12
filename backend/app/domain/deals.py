from app.domain.boosters import BoosterShelfEntry


class Deals:
    def __init__(self) -> None:
        self.bought_deals: set[str] = set()
        self.token_spent: int = 0
        self.usdt_spent: int = 0
        self.ton_spent: int = 0
        self.boosters: list[BoosterShelfEntry] = []
