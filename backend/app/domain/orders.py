from datetime import datetime


class Order:
    def __init__(
        self,
        items: dict[str, int],
        price: int,
        start_timestamp: datetime,
        token_price: int,
    ) -> None:
        self.items = items
        self.price = price
        self.token_price = token_price
        self.start_timestamp = start_timestamp
        self.completed = False
