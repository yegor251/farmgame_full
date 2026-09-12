import hashlib
import hmac
import time
from urllib.parse import quote

import pytest

from app.auth.telegram_init_data import TelegramInitDataValidator

BOT_TOKEN = "123456:test-bot-token"


def _build_init_data(*, user_id: int = 42, auth_date: int | None = None, tamper: bool = False) -> str:
    if auth_date is None:
        auth_date = int(time.time())

    fields = {
        "user": f'{{"id":{user_id},"first_name":"Test"}}',
        "auth_date": str(auth_date),
        "query_id": "AAabc123",
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    received_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if tamper:
        received_hash = "0" * len(received_hash)

    fields["hash"] = received_hash
    return "&".join(f"{key}={quote(value, safe='')}" for key, value in fields.items())


def test_check_returns_user_id_for_valid_signature() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)

    result = validator.check(_build_init_data(user_id=42))

    assert result == "42"


def test_check_rejects_tampered_hash() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)

    result = validator.check(_build_init_data(tamper=True))

    assert result is None


@pytest.mark.parametrize("init_data", ["", "hash=only", "user=%7B%22id%22%3A1%7D"])
def test_check_rejects_missing_hash_or_user(init_data: str) -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)

    assert validator.check(init_data) is None


def test_check_rejects_expired_signature_when_ttl_configured() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN, ttl_seconds=60)
    stale_init_data = _build_init_data(auth_date=int(time.time()) - 3600)

    assert validator.check(stale_init_data) is None


def test_check_accepts_signature_within_ttl() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN, ttl_seconds=3600)

    result = validator.check(_build_init_data(user_id=7))

    assert result == "7"


def test_check_ignores_ttl_when_not_configured() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)
    old_init_data = _build_init_data(auth_date=0)

    assert validator.check(old_init_data) == "42"


def test_check_accepts_plain_numeric_tg_id_as_dev_fallback() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)

    assert validator.check("2357501") == "2357501"
