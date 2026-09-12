import random
from datetime import UTC, datetime, timedelta

from app.config import settings
from app.domain.player import Player
from app.domain.spin import Spin
from app.errors import GameErrorCode


def generate_spin(player: Player) -> int:
    keyset = player.inventory.pull_random(5)
    items: list[tuple[str, int]] = [(name, random.randint(1, 6)) for name in keyset]
    items.append(("money", random.randint(10, 50)))
    player.spin = Spin(items, items[random.randint(0, 5)])
    return GameErrorCode.OK


def regenerate(player: Player) -> int:
    spin_deadline = player.spin.generate_timestamp + timedelta(seconds=settings.spin_time_to_spin_seconds)
    if spin_deadline < datetime.now(UTC):
        return generate_spin(player)
    return GameErrorCode.SPIN_NOT_READY


def spin_wheel(player: Player) -> int:
    spin = player.spin
    if spin is None:
        return GameErrorCode.SPIN_NOT_GENERATED

    if spin.activated:
        return GameErrorCode.SPIN_NOT_READY

    spin_deadline = spin.generate_timestamp + timedelta(seconds=settings.spin_time_to_spin_seconds)
    if spin_deadline < datetime.now(UTC):
        return GameErrorCode.CANNOT_USE_BUILDING

    drop_item, drop_amount = spin.drop
    if drop_item == "money":
        player.money += drop_amount
    else:
        player.inventory.add_amount(drop_item, drop_amount)
    spin.activated = True
    return GameErrorCode.OK
