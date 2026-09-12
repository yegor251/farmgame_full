from app.domain.obstacle import Obstacle
from app.domain.player import Player


def test_get_name_returns_obstacle_type() -> None:
    assert Obstacle("stone_small").get_name() == "stone_small"


def test_requeue_is_a_noop(player: Player) -> None:
    obstacle = Obstacle("stone_small")

    assert obstacle.requeue(player) is None
