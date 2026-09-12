import random


class ItemContainer:
    def __init__(self) -> None:
        self.items: dict[str, int] = {}
        self.items_amount: int = 0
        self.capacity: int = 70
        self.level: int = 0

    def get_amount(self, item: str) -> int | None:
        return self.items.get(item)

    def enlarge_capacity(self, amount: int) -> None:
        self.capacity += amount

    def check_amount(self, amount: int) -> bool:
        return (self.items_amount + amount) <= self.capacity

    def check_map(self, items: dict[str, int]) -> bool:
        total_amount = sum(items.values())
        return (total_amount + self.items_amount) <= self.capacity

    def add_map(self, items: dict[str, int]) -> None:
        if self.check_map(items):
            for name, amount in items.items():
                self.add_amount_unchecked(name, amount)

    def add_map_unchecked(self, items: dict[str, int]) -> None:
        for name, amount in items.items():
            self.add_amount_unchecked(name, amount)

    def add_amount_unchecked(self, item: str, amount: int) -> None:
        self.items[item] = self.items.get(item, 0) + amount
        self.items_amount += amount

    def add_amount(self, item: str, amount: int) -> None:
        if self.check_amount(amount):
            self.items[item] = self.items.get(item, 0) + amount
            self.items_amount += amount

    def pull_random(self, amount: int) -> list[str]:
        if not self.items:
            return []
        keys = list(self.items.keys())
        return [random.choice(keys) for _ in range(amount)]

    def pull_random_unique(self, amount: int = 1) -> set[str]:
        if not self.items:
            return set()
        keys = list(self.items.keys())
        random.shuffle(keys)
        return set(keys[: min(amount, len(keys))])
