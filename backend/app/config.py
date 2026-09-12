from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FARMGAME_", env_file=".env", extra="ignore")

    bot_token: str = "7734943379:AAGF2_IbH6ZgMqU9T5o-WOzQsBLbjTWR4xU"
    init_data_ttl_seconds: int | None = None

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_pass: str = "postgres"
    database_url: str | None = None

    resources_dir: Path = Path(__file__).resolve().parent.parent / "resources"
    sessions_dir: Path = Path(__file__).resolve().parent.parent / "sessions"

    ws_host: str = "0.0.0.0"
    ws_port: int = 8000

    debug: bool = False

    max_strikes: int = 5

    map_size_x: int = 30
    map_size_y: int = 30

    spin_time_to_spin_seconds: int = 28800

    orders_reroll_time_seconds: int = 60
    orders_amount_min: int = 3
    orders_amount_max: int = 5
    orders_regeneration_time_seconds: int = 60

    max_purchased_slots: int = 3
    purchased_slots_price: tuple[int, ...] = (1000, 10000, 100000)

    building_bakery_per_building_k: float = 100.0
    building_corral_per_building_k: float = 100.0
    building_garden_per_building_k: float = 1.2

    withdraw_ton_fee: int = 100_000_000

    @property
    def database_dsn(self) -> str:
        if self.database_url is not None:
            return self.database_url
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
