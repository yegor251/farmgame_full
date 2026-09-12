from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class DepositWatcherSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FARMGAME_CRYPTO_", env_file=".env", extra="ignore")

    tonapi_key: str = ""
    tonapi_base_url: str = "https://tonapi.io"

    hot_wallet_account_id: str
    usdt_jetton_address: str
    tfc_jetton_address: str

    deposit_cursor_file: Path = _BACKEND_ROOT / "deposit_cursor.txt"
    deposit_events_limit: int = 100
    deposit_poll_interval_seconds: int = 10


class WithdrawProcessorSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FARMGAME_CRYPTO_", env_file=".env", extra="ignore")

    tonapi_key: str = ""
    tonapi_base_url: str = "https://tonapi.io"

    hot_wallet_mnemonic: str
    withdraw_jetton_master_address: str

    toncenter_base_url: str = "https://toncenter.com/api/v2"
    toncenter_api_key: str = ""

    withdraw_gas_ton: float = 0.05
    withdraw_batch_limit: int = 100
    withdraw_poll_interval_seconds: int = 5
    withdraw_idle_sleep_seconds: int = 20
