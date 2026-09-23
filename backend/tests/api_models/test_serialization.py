import json

import pytest
from pydantic import ValidationError

from app.api_models.boosters import ActiveBoosterResponse, ActiveBoostersResponse, BoosterShelfResponse
from app.api_models.deal import DealResponse, RewardResponse
from app.api_models.game_session import GameSessionResponse, OperationResponse
from app.api_models.item_container import ItemsContainerResponse
from app.api_models.order import OrderResponse
from app.api_models.player import PlayerResponse
from app.api_models.spin import SlotResponse, SpinResponse
from app.api_models.transaction import DepositResponse
from app.api_models.wallet import WalletResponse
from app.api_models.world import BuildingResponse, BuildingSlotResponse, WorldResponse


def _dump(model: object) -> dict:
    return json.loads(model.model_dump_json(by_alias=True, exclude_none=True))  # type: ignore[attr-defined]


def test_player_response_uses_capitalized_inventory_and_lowercase_networth() -> None:
    player = PlayerResponse(
        money=100,
        networth=50,
        inventory=ItemsContainerResponse(map={"wheat": 1}, level=0),
    )

    payload = _dump(player)

    assert payload["networth"] == 50
    assert "netWorth" not in payload
    assert payload["Inventory"] == {"map": {"wheat": 1}, "level": 0}
    assert "spin" not in payload
    assert "orders" not in payload


def test_wallet_response_aliases_are_camel_case() -> None:
    wallet = WalletResponse(usdt_balance=1, ton_balance=2, token_balance=3)

    payload = _dump(wallet)

    assert payload == {"usdtBalance": 1, "tonBalance": 2, "tokenBalance": 3}


def test_active_boosters_response_uses_pascal_case_keys_and_omits_none() -> None:
    active = ActiveBoostersResponse(
        order_money=ActiveBoosterResponse(percentage=20, time=3600, activate_time_stamp=1000)
    )

    payload = _dump(active)

    assert payload == {"OrderMoney": {"percentage": 20, "time": 3600, "activateTimeStamp": 1000}}
    assert "OrderItems" not in payload
    assert "WorkSpeed" not in payload
    assert "GrowSpeed" not in payload


def test_building_response_aliases_slot_and_building_fields() -> None:
    building = BuildingResponse(
        name="bakery1",
        x=1,
        y=2,
        slots=[
            BuildingSlotResponse(
                work_name="bread", work_start_time_stamp=100, work_end_time_stamp=200
            )
        ],
        integer_data=3,
        level=1,
    )

    payload = _dump(building)

    assert payload["slots"][0] == {
        "workName": "bread",
        "workStartTimeStamp": 100,
        "workEndTimeStamp": 200,
    }
    assert payload["integerData"] == 3


def test_world_response_uses_tile_array_alias() -> None:
    world = WorldResponse(tile_array=[])

    payload = _dump(world)

    assert payload == {"tileArray": []}


def test_deposit_response_stays_snake_case_even_with_by_alias() -> None:
    deposit = DepositResponse(
        transaction_id=1,
        active=True,
        tg_id=42,
        amount=100,
        time_stamp=1000,
        jetton_signature="sig",
        commentary="note",
    )

    assert _dump(deposit) == {
        "transaction_id": 1,
        "active": True,
        "tg_id": 42,
        "amount": 100,
        "time_stamp": 1000,
        "jetton_signature": "sig",
        "commentary": "note",
    }


def test_deal_response_prices_are_camel_case_and_omit_when_none() -> None:
    deal = DealResponse(name="starter", ton_price=100, reward=RewardResponse(money=50))

    payload = _dump(deal)

    assert payload["tonPrice"] == 100
    assert "tokenPrice" not in payload
    assert "usdtPrice" not in payload
    assert payload["reward"] == {"money": 50}


def test_reward_response_preserves_empty_booster_list_distinct_from_omitted() -> None:
    reward_with_empty_boosters = RewardResponse(money=10, boosters=[])
    reward_without_boosters = RewardResponse(money=10)

    assert _dump(reward_with_empty_boosters)["boosters"] == []
    assert "boosters" not in _dump(reward_without_boosters)


def test_game_session_response_always_sends_empty_businesses_array() -> None:
    session = GameSessionResponse(
        data_type="game-session-regen",
        player=PlayerResponse(
            money=1, networth=1, inventory=ItemsContainerResponse(map={}, level=0)
        ),
        wallet=WalletResponse(usdt_balance=0, ton_balance=0, token_balance=0),
        active_boosters=ActiveBoostersResponse(),
        ref_amount=0,
    )

    payload = _dump(session)

    assert payload["businesses"] == []
    assert payload["dataType"] == "game-session-regen"
    assert payload["refAmount"] == 0
    assert "world" not in payload
    assert "deposits" not in payload
    assert "availableDeals" not in payload


def test_operation_response_defaults_to_result_code_data_type() -> None:
    response = OperationResponse(code=-1001)

    payload = _dump(response)

    assert payload == {"dataType": "result-code", "code": -1001}


def test_spin_and_order_response_aliases() -> None:
    spin = SpinResponse(
        items=[SlotResponse(item="wheat", amount=1)],
        drop=SlotResponse(item="money", amount=10),
        generate_time_stamp=123,
        activated=True,
    )
    order = OrderResponse(
        order_items={"bread": 1}, order_price=15, order_token_price=0, completed=False, time_stamp=456
    )

    assert _dump(spin)["generateTimeStamp"] == 123
    assert _dump(order) == {
        "orderItems": {"bread": 1},
        "orderPrice": 15,
        "orderTokenPrice": 0,
        "completed": False,
        "timeStamp": 456,
    }


def test_player_response_missing_required_field_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        PlayerResponse(money=1, inventory=ItemsContainerResponse(map={}, level=0))  # type: ignore[call-arg]


def test_booster_shelf_response_wrong_type_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        BoosterShelfResponse(booster_type="WorkSpeed", percentage="not-an-int", time=10)  # type: ignore[arg-type]
