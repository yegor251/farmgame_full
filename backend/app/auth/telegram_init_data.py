import hashlib
import hmac
import time
from urllib.parse import unquote


class TelegramInitDataValidator:
    def __init__(self, bot_token: str, ttl_seconds: int | None = None) -> None:
        self._bot_token = bot_token
        self._ttl_seconds = ttl_seconds

    def _parse(self, init_data: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for pair in init_data.split("&"):
            key_value = pair.split("=")
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

    def check(self, init_data: str) -> str | None:
        if init_data.isdigit():
            return init_data

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

        return self._parse_user_id(parsed["user"])
