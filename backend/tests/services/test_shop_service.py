from app.domain.player import Player
from app.errors import GameErrorCode
from app.services import shop_service


def test_validate_purchase_rejects_already_bought_deal() -> None:
    player = Player()
    player.deals.bought_deals.add("additionalToken_ton")

    result = shop_service.validate_purchase(player, "additionalToken_ton")

    assert result == GameErrorCode.DEAL_HAS_BEEN_ALREADY_BOUGHT


def test_validate_purchase_rejects_unknown_deal() -> None:
    player = Player()

    assert shop_service.validate_purchase(player, "not-a-deal") == GameErrorCode.SOCKET_WRONG_FORMAT


def test_validate_purchase_rejects_when_not_enough_funds() -> None:
    player = Player()

    result = shop_service.validate_purchase(player, "additionalToken_ton")

    assert result == GameErrorCode.NOT_ENOUGH_MONEY


def test_validate_purchase_charges_wallet_and_tracks_spend_on_success() -> None:
    player = Player()
    player.wallet.ton_balance = 1_000_000_000

    result = shop_service.validate_purchase(player, "additionalToken_ton")

    assert result == GameErrorCode.OK
    assert player.wallet.ton_balance == 800_000_000
    assert player.deals.ton_spent == 200_000_000


def test_purchase_deal_grants_token_reward_and_marks_bought() -> None:
    player = Player()
    player.wallet.ton_balance = 1_000_000_000

    result = shop_service.purchase_deal(player, "additionalToken_ton")

    assert result == GameErrorCode.OK
    assert player.wallet.token_balance == 5000
    assert "additionalToken_ton" in player.deals.bought_deals


def test_purchase_deal_adds_booster_shelf_entries() -> None:
    player = Player()
    player.wallet.ton_balance = 1_000_000_000

    result = shop_service.purchase_deal(player, "boosterX4_ton")

    assert result == GameErrorCode.OK
    assert {b.booster_type for b in player.deals.boosters} == {
        "WorkSpeed",
        "OrderItems",
        "OrderMoney",
        "GrowSpeed",
    }


def test_purchase_deal_propagates_validation_failure_without_side_effects() -> None:
    player = Player()

    result = shop_service.purchase_deal(player, "additionalToken_ton")

    assert result == GameErrorCode.NOT_ENOUGH_MONEY
    assert player.wallet.token_balance == 0
    assert "additionalToken_ton" not in player.deals.bought_deals


def test_buy_rejects_unknown_plant() -> None:
    player = Player()

    assert shop_service.buy("not-a-plant", 1, player) == GameErrorCode.SOCKET_WRONG_FORMAT


def test_buy_rejects_non_positive_amount() -> None:
    player = Player()

    assert shop_service.buy("wheat", 0, player) == GameErrorCode.INVALID_AMOUNT


def test_buy_rejects_when_not_enough_money() -> None:
    player = Player()
    player.money = 0

    assert shop_service.buy("wheat", 1, player) == GameErrorCode.NOT_ENOUGH_MONEY


def test_buy_rejects_when_inventory_has_no_space() -> None:
    player = Player()
    player.money = 10_000
    player.inventory.capacity = 0

    assert shop_service.buy("wheat", 1, player) == GameErrorCode.NO_SPACE_IN_INVENTORY


def test_buy_deducts_money_and_adds_seeds_on_success() -> None:
    player = Player()
    player.money = 100

    result = shop_service.buy("wheat", 2, player)

    assert result == GameErrorCode.OK
    assert player.money == 80
    assert player.inventory.items["wheat"] == 2
