from datetime import UTC, datetime


class Spin:
    def __init__(self, items: list[tuple[str, int]], drop: tuple[str, int]) -> None:
        self.items = items
        self.drop = drop
        self.activated = False
        self.generate_timestamp = datetime.now(UTC)
