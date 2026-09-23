from typing import Protocol

from app.crypto.ton_api_models import AccountEvent


class EventsSource(Protocol):
    async def get_account_events(
        self, account_id: str, limit: int, start_date: int
    ) -> list[AccountEvent]: ...
