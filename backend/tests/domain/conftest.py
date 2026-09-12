import pytest

from app.domain.player import Player


@pytest.fixture
def player() -> Player:
    return Player()
