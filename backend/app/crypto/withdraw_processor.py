import asyncio
import logging

from app.crypto.contracts import JettonTransferSigner, JettonWalletResolver, TonNetworkClient
from app.domain.transfer_info import Withdraw
from app.persistence.contracts import WithdrawRepository

logger = logging.getLogger(__name__)


class WithdrawProcessor:
    def __init__(
        self,
        wallet: JettonTransferSigner,
        toncenter_client: TonNetworkClient,
        jetton_wallet_resolver: JettonWalletResolver,
        withdraw_repository: WithdrawRepository,
        jetton_master_address: str,
        gas_ton: float,
        batch_limit: int,
        retry_interval_seconds: int,
        idle_sleep_seconds: int,
    ) -> None:
        self._wallet = wallet
        self._toncenter_client = toncenter_client
        self._jetton_wallet_resolver = jetton_wallet_resolver
        self._withdraw_repository = withdraw_repository
        self._jetton_master_address = jetton_master_address
        self._gas_ton = gas_ton
        self._batch_limit = batch_limit
        self._retry_interval_seconds = retry_interval_seconds
        self._idle_sleep_seconds = idle_sleep_seconds
        self._jetton_wallet_address: str | None = None

    async def _resolve_jetton_wallet_address(self) -> str:
        if self._jetton_wallet_address is None:
            address = await self._jetton_wallet_resolver.get_jetton_wallet_address(
                self._wallet.address, self._jetton_master_address
            )
            if address is None:
                raise RuntimeError("Hot wallet has no jetton wallet for the configured jetton master")
            self._jetton_wallet_address = address
        return self._jetton_wallet_address

    async def _send_until_confirmed(self, withdraw: Withdraw, jetton_wallet_address: str) -> None:
        seqno = await self._toncenter_client.get_seqno(self._wallet.address)
        while True:
            current_seqno = await self._toncenter_client.get_seqno(self._wallet.address)
            if current_seqno > seqno:
                logger.info("Withdraw %s confirmed", withdraw.transaction_id)
                return
            boc = self._wallet.build_jetton_transfer_boc(
                jetton_wallet_address=jetton_wallet_address,
                to_address=withdraw.wallet,
                jetton_amount=withdraw.amount,
                seqno=seqno,
                gas_ton=self._gas_ton,
            )
            try:
                await self._toncenter_client.send_boc(boc)
            except Exception:
                logger.exception("Failed to broadcast withdraw %s", withdraw.transaction_id)
            await asyncio.sleep(self._retry_interval_seconds)

    async def run(self) -> None:
        jetton_wallet_address = await self._resolve_jetton_wallet_address()
        while True:
            pending = await self._withdraw_repository.list_pending_withdraws(self._batch_limit)
            if not pending:
                await asyncio.sleep(self._idle_sleep_seconds)
                continue
            for withdraw in pending:
                await self._withdraw_repository.mark_withdraw_sent(withdraw.transaction_id)
                try:
                    await self._send_until_confirmed(withdraw, jetton_wallet_address)
                except Exception:
                    logger.exception("Withdraw %s processing failed", withdraw.transaction_id)
