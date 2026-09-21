import hashlib
import hmac
import time
from urllib.parse import unquote

from pydantic import BaseModel


class TelegramAuthResult(BaseModel):
    tg_id: int
    is_verified: bool
    ref_id: int = 0


class TelegramInitDataValidator:
    def __init__(self, bot_token: str, ttl_seconds: int | None = None, dev_fallback_tg_id: int = 0) -> None:
        self._bot_token = bot_token
        self._ttl_seconds = ttl_seconds
        self._dev_fallback_tg_id = dev_fallback_tg_id

    def _parse(self, init_data: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for pair in init_data.split("&"):
            key_value = pair.split("=", 1)
            if len(key_value) != 2:
                continue
            key, value = key_value
            parsed[unquote(key)] = unquote(value)
        return parsed

    def _parse_user_id(self, raw_user: str) -> str | None:
        body = raw_user.removeprefix("{").removesuffix("}")
        fields: dict[str, str] = {}
        for pair in body.split(","):
            key_value = pair.split(":", 1)
            if len(key_value) != 2:
                continue
            key, value = (part.strip() for part in key_value)
            fields[key.strip('"')] = value.strip('"')
        return fields.get("id")

    def check(self, init_data: str) -> TelegramAuthResult | None:
        if init_data.isdigit():
            return TelegramAuthResult(tg_id=self._dev_fallback_tg_id, is_verified=False)

        parsed = self._parse(init_data)
        if "hash" not in parsed or "user" not in parsed:
            return None

        received_hash = parsed["hash"]
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(parsed.items()) if key != "hash"
        )

        secret_key = hmac.new(b"WebAppData", self._bot_token.encode("utf-8"), hashlib.sha256).digest()
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        if calculated_hash != received_hash:
            return None

        if self._ttl_seconds is not None and "auth_date" in parsed:
            try:
                auth_date = int(parsed["auth_date"])
            except ValueError:
                return None
            if time.time() - auth_date > self._ttl_seconds:
                return None

        user_id = self._parse_user_id(parsed["user"])
        if user_id is None or not user_id.isdigit():
            return None

        start_param = parsed.get("start_param", "")
        ref_id = int(start_param) if start_param.isdigit() else 0

        return TelegramAuthResult(tg_id=int(user_id), is_verified=True, ref_id=ref_id)
