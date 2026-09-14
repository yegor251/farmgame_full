import hashlib
import hmac
import time
from urllib.parse import quote

import pytest

from app.auth.telegram_init_data import TelegramAuthResult, TelegramInitDataValidator

BOT_TOKEN = "123456:test-bot-token"


def _build_init_data(
    *,
    user_id: int = 42,
    auth_date: int | None = None,
    tamper: bool = False,
    start_param: str | None = None,
) -> str:
    if auth_date is None:
        auth_date = int(time.time())

    fields = {
        "user": f'{{"id":{user_id},"first_name":"Test"}}',
        "auth_date": str(auth_date),
        "query_id": "AAabc123",
    }
    if start_param is not None:
        fields["start_param"] = start_param
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    received_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if tamper:
        received_hash = "0" * len(received_hash)

    fields["hash"] = received_hash
    return "&".join(f"{key}={quote(value, safe='')}" for key, value in fields.items())


def test_check_returns_verified_result_for_valid_signature() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)

    result = validator.check(_build_init_data(user_id=42))

    assert result == TelegramAuthResult(tg_id=42, is_verified=True, ref_id=0)


def test_check_extracts_ref_id_from_start_param() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)

    result = validator.check(_build_init_data(user_id=42, start_param="777"))

    assert result == TelegramAuthResult(tg_id=42, is_verified=True, ref_id=777)


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

    assert result == TelegramAuthResult(tg_id=7, is_verified=True, ref_id=0)


def test_check_ignores_ttl_when_not_configured() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN)
    old_init_data = _build_init_data(auth_date=0)

    result = validator.check(old_init_data)

    assert result == TelegramAuthResult(tg_id=42, is_verified=True, ref_id=0)


def test_check_maps_plain_numeric_input_to_configured_dev_fallback() -> None:
    validator = TelegramInitDataValidator(BOT_TOKEN, dev_fallback_tg_id=2357501)

    result = validator.check("999999999")

    assert result == TelegramAuthResult(tg_id=2357501, is_verified=False, ref_id=0)
