from datetime import UTC, datetime, timedelta

from app.domain.player import Player
from app.domain.spin import Spin
from app.errors import GameErrorCode
from app.services import spin_service


def test_generate_spin_replaces_player_spin_with_six_items_and_a_drop() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 5)
    player.inventory.add_amount("bread", 5)

    result = spin_service.generate_spin(player)

    assert result == GameErrorCode.OK
    assert len(player.spin.items) == 6
    assert player.spin.drop in player.spin.items
    assert player.spin.activated is False


def test_regenerate_rejects_when_spin_not_yet_due() -> None:
    player = Player()

    assert spin_service.regenerate(player) == GameErrorCode.SPIN_NOT_READY


def test_regenerate_generates_new_spin_when_due() -> None:
    player = Player()
    player.inventory.add_amount("wheat", 4)
    player.spin.generate_timestamp = datetime.now(UTC) - timedelta(days=1)

    result = spin_service.regenerate(player)

    assert result == GameErrorCode.OK
    assert player.spin.activated is False


def test_spin_wheel_rejects_when_already_activated() -> None:
    player = Player()
    player.spin.activated = True

    assert spin_service.spin_wheel(player) == GameErrorCode.SPIN_NOT_READY


def test_spin_wheel_rejects_when_deadline_has_passed() -> None:
    player = Player()
    player.spin.generate_timestamp = datetime.now(UTC) - timedelta(days=1)

    assert spin_service.spin_wheel(player) == GameErrorCode.CANNOT_USE_BUILDING


def test_spin_wheel_grants_money_drop_and_marks_activated() -> None:
    player = Player()
    player.spin = Spin([("money", 10)], ("money", 25))
    money_before = player.money

    result = spin_service.spin_wheel(player)

    assert result == GameErrorCode.OK
    assert player.money == money_before + 25
    assert player.spin.activated is True


def test_spin_wheel_grants_item_drop() -> None:
    player = Player()
    player.spin = Spin([("wheat", 4)], ("wheat", 4))

    result = spin_service.spin_wheel(player)

    assert result == GameErrorCode.OK
    assert player.inventory.items["wheat"] == 4
