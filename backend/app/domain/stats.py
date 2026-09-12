class Stats:
    def __init__(self, building_names: list[str]) -> None:
        self.orders_completed: int = 0
        self.buildings_placed: dict[str, int] = dict.fromkeys(building_names, 0)
