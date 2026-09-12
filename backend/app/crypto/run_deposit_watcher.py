import asyncio
import logging

from app.config import settings
from app.crypto.config import DepositWatcherSettings
from app.crypto.deposit_cursor import DepositCursorStore
from app.crypto.deposit_watcher import DepositWatcher
from app.crypto.ton_api_client import TonApiClient
from app.persistence.db import session_scope
from app.persistence.repository import SqlDepositRepository

logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)


async def main() -> None:
    crypto_settings = DepositWatcherSettings()
    ton_client = TonApiClient(crypto_settings.tonapi_base_url, crypto_settings.tonapi_key)
    cursor_store = DepositCursorStore(crypto_settings.deposit_cursor_file)

    try:
        async with session_scope() as session:
            watcher = DepositWatcher(
                ton_client=ton_client,
                deposit_repository=SqlDepositRepository(session),
                cursor_store=cursor_store,
                account_id=crypto_settings.hot_wallet_account_id,
                usdt_jetton_address=crypto_settings.usdt_jetton_address,
                tfc_jetton_address=crypto_settings.tfc_jetton_address,
                events_limit=crypto_settings.deposit_events_limit,
                poll_interval_seconds=crypto_settings.deposit_poll_interval_seconds,
            )
            await watcher.run()
    finally:
        await ton_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
