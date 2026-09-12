from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.player import Player


class Buildable(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def requeue(self, player: "Player") -> None: ...
