from typing import TYPE_CHECKING

from app.domain.buildable import Buildable

if TYPE_CHECKING:
    from app.domain.player import Player


class Obstacle(Buildable):
    def __init__(self, name: str) -> None:
        self.obstacle_type = name

    def get_name(self) -> str:
        return self.obstacle_type

    def requeue(self, player: "Player") -> None:
        return None
