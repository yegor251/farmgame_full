from app.domain.boosters import BoosterShelfEntry
from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import booster_service


def test_activate_by_index_rejects_negative_index() -> None:
    player = Player()

    assert booster_service.activate_by_index(player, -1) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_activate_by_index_rejects_out_of_range_index() -> None:
    player = Player()

    assert booster_service.activate_by_index(player, 0) == GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES


def test_activate_by_index_pops_shelf_entry_and_activates_it() -> None:
    player = Player()
    player.deals.boosters.append(BoosterShelfEntry(booster_type="WorkSpeed", percentage=50, time=3600))

    result = booster_service.activate_by_index(player, 0)

    assert result == GameErrorCode.OK
    assert player.deals.boosters == []
    assert player.active_boosters.work_speed is not None
    assert player.active_boosters.work_speed.percentage == 50
