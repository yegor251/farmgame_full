from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import ambar_service
from app.static_data.catalog import get_catalog


def test_upgrade_inventory_rejects_when_already_at_max_level() -> None:
    player = Player()
    player.inventory.level = len(get_catalog().ambar.levels)

    assert ambar_service.upgrade_inventory(player) == GameErrorCode.BUILDING_ALREADY_MAXXED_UP


def test_upgrade_inventory_rejects_when_not_enough_tokens() -> None:
    player = Player()
    player.wallet.token_balance = 0

    assert ambar_service.upgrade_inventory(player) == GameErrorCode.NOT_ENOUGH_MONEY


def test_upgrade_inventory_charges_tokens_and_enlarges_capacity_on_success() -> None:
    player = Player()
    player.wallet.token_balance = 1_000
    capacity_before = player.inventory.capacity

    result = ambar_service.upgrade_inventory(player)

    assert result == GameErrorCode.OK
    assert player.inventory.level == 1
    assert player.inventory.capacity == capacity_before + 10
    assert player.wallet.token_balance == 900
