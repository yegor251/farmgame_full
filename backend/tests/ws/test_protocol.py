import hashlib
import hmac
import time
from urllib.parse import quote

import pytest

from app.auth.telegram_init_data import TelegramAuthResult, TelegramInitDataValidator
from app.ws import protocol

BOT_TOKEN = "123456:test-bot-token"


def _valid_init_data(user_id: int = 42) -> str:
    fields = {
        "user": f'{{"id":{user_id},"first_name":"Test"}}',
        "auth_date": str(int(time.time())),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return "&".join(f"{key}={quote(value, safe='')}" for key, value in fields.items())


@pytest.fixture
def validator() -> TelegramInitDataValidator:
    return TelegramInitDataValidator(BOT_TOKEN)


def test_parse_connect_with_valid_init_data(validator: TelegramInitDataValidator) -> None:
    command = protocol.parse_command(f"connect/{_valid_init_data(42)}", validator)

    assert command == protocol.Connect(auth=TelegramAuthResult(tg_id=42, is_verified=True, ref_id=0))


def test_parse_connect_with_invalid_init_data(validator: TelegramInitDataValidator) -> None:
    command = protocol.parse_command("connect/not-a-valid-init-data", validator)

    assert command == protocol.Connect(auth=None)


def test_parse_literal_commands(validator: TelegramInitDataValidator) -> None:
    assert protocol.parse_command("spin", validator) == protocol.SpinWheel()
    assert protocol.parse_command("regen", validator) == protocol.Regeneration()
    assert protocol.parse_command("invupgrade", validator) == protocol.InvUpgrade()


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("use/wheat/1/2", protocol.Use(name="wheat", x=1, y=2)),
        ("collect/3/4", protocol.Collect(x=3, y=4)),
        ("upgrade/5/6", protocol.Upgrade(x=5, y=6)),
        ("buy/wheat/10", protocol.Buy(name="wheat", amount=10)),
        ("order/complete/0", protocol.OrderOperation(operation="complete", index=0)),
        ("place/garden/1/1", protocol.Place(name="garden", x=1, y=1)),
        ("move/1/2/3/4", protocol.Move(x=1, y=2, to_x=3, to_y=4)),
        ("claim/2", protocol.ClaimDeposit(index=2)),
        ("withdraw/100/EQ...wallet", protocol.RegisterWithdraw(amount=100, wallet="EQ...wallet")),
        ("buyslot/1/2", protocol.PurchaseSlot(x=1, y=2)),
        ("buydeal/starter", protocol.PurchaseDeal(name="starter")),
        ("activateb/3", protocol.ActivateBooster(index=3)),
        ("rmobstacle/7/8", protocol.RemoveObstacle(x=7, y=8)),
    ],
)
def test_parse_well_formed_commands(
    validator: TelegramInitDataValidator, message: str, expected: protocol.Command
) -> None:
    assert protocol.parse_command(message, validator) == expected


@pytest.mark.parametrize(
    "message",
    [
        "use/wheat/1",
        "collect/notanumber/4",
        "place/garden/1",
        "move/1/2/3",
        "unknownevent/1/2",
        "ping",
        "",
    ],
)
def test_parse_malformed_or_unknown_commands_fall_back_to_unknown(
    validator: TelegramInitDataValidator, message: str
) -> None:
    assert protocol.parse_command(message, validator) == protocol.Unknown()


def test_business_commands_are_not_parsed(validator: TelegramInitDataValidator) -> None:
    assert protocol.parse_command("business/buy/farm", validator) == protocol.Unknown()
