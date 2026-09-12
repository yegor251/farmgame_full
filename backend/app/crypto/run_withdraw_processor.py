import asyncio
import logging

from app.config import settings
from app.crypto.config import WithdrawProcessorSettings
from app.crypto.ton_api_client import TonApiClient
from app.crypto.toncenter_client import ToncenterClient
from app.crypto.wallet import HotWallet
from app.crypto.withdraw_processor import WithdrawProcessor
from app.persistence.db import session_scope
from app.persistence.repository import SqlWithdrawRepository

logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)


async def main() -> None:
    crypto_settings = WithdrawProcessorSettings()
    wallet = HotWallet(crypto_settings.hot_wallet_mnemonic)
    ton_api_client = TonApiClient(crypto_settings.tonapi_base_url, crypto_settings.tonapi_key)
    toncenter_client = ToncenterClient(
        crypto_settings.toncenter_base_url, crypto_settings.toncenter_api_key
    )

    try:
        async with session_scope() as session:
            processor = WithdrawProcessor(
                wallet=wallet,
                toncenter_client=toncenter_client,
                jetton_wallet_resolver=ton_api_client,
                withdraw_repository=SqlWithdrawRepository(session),
                jetton_master_address=crypto_settings.withdraw_jetton_master_address,
                gas_ton=crypto_settings.withdraw_gas_ton,
                batch_limit=crypto_settings.withdraw_batch_limit,
                retry_interval_seconds=crypto_settings.withdraw_poll_interval_seconds,
                idle_sleep_seconds=crypto_settings.withdraw_idle_sleep_seconds,
            )
            await processor.run()
    finally:
        await ton_api_client.aclose()
        await toncenter_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
