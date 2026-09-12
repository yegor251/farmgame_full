from app.domain import boosters
from app.domain.player import Player
from app.errors import GameErrorCode


def activate_by_index(player: Player, index: int) -> int:
    if index < 0 or index >= len(player.deals.boosters):
        return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES

    shelf_entry = player.deals.boosters.pop(index)
    boosters.activate(player.active_boosters, shelf_entry)
    return GameErrorCode.OK
