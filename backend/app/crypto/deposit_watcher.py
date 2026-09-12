import asyncio
import logging

from app.crypto.contracts import EventsSource
from app.crypto.deposit_cursor import DepositCursorState, DepositCursorStore
from app.crypto.ton_api_models import AccountEvent, EventAction
from app.domain.transfer_info import Deposit
from app.persistence.contracts import DepositRepository

logger = logging.getLogger(__name__)

EVENT_ID_MODULO = 9223372036854775807


class DepositWatcher:
    def __init__(
        self,
        ton_client: EventsSource,
        deposit_repository: DepositRepository,
        cursor_store: DepositCursorStore,
        account_id: str,
        usdt_jetton_address: str,
        tfc_jetton_address: str,
        events_limit: int,
        poll_interval_seconds: int,
    ) -> None:
        self._ton_client = ton_client
        self._deposit_repository = deposit_repository
        self._cursor_store = cursor_store
        self._account_id = account_id
        self._usdt_jetton_address = usdt_jetton_address
        self._tfc_jetton_address = tfc_jetton_address
        self._events_limit = events_limit
        self._poll_interval_seconds = poll_interval_seconds
        self._cursor = cursor_store.load()

    @staticmethod
    def _extract_tg_id(comment: str) -> int:
        stripped = comment.lstrip("-")
        if not stripped or not stripped.isdigit():
            return -1
        return int(comment)

    def _jetton_signature(self, jetton_address: str) -> str | None:
        if jetton_address == self._usdt_jetton_address:
            return "USD"
        if jetton_address == self._tfc_jetton_address:
            return "TFC"
        return None

    @staticmethod
    def _event_transaction_id(event: AccountEvent) -> int:
        return int(event.event_id, 16) % EVENT_ID_MODULO

    def _deposit_from_action(
        self, action: EventAction, transaction_id: int, timestamp: int
    ) -> Deposit | None:
        if action.TonTransfer is not None and action.TonTransfer.recipient.address == self._account_id:
            transfer = action.TonTransfer
            return Deposit(
                transaction_id=transaction_id,
                active=True,
                tg_id=self._extract_tg_id(transfer.comment),
                amount=transfer.amount,
                time_stamp=timestamp,
                jetton_signature="TON",
                commentary="donation",
            )
        if (
            action.JettonTransfer is not None
            and action.JettonTransfer.recipient.address == self._account_id
        ):
            jetton_transfer = action.JettonTransfer
            signature = self._jetton_signature(jetton_transfer.jetton.address)
            if signature is None:
                return None
            return Deposit(
                transaction_id=transaction_id,
                active=True,
                tg_id=self._extract_tg_id(jetton_transfer.comment),
                amount=jetton_transfer.amount,
                time_stamp=timestamp,
                jetton_signature=signature,
                commentary="donation",
            )
        return None

    def _extract_new_deposits(self, events: list[AccountEvent]) -> list[Deposit]:
        deposits: list[Deposit] = []
        for event in events:
            transaction_id = self._event_transaction_id(event)
            if transaction_id == self._cursor.last_transaction_id:
                break
            for action in event.actions:
                deposit = self._deposit_from_action(action, transaction_id, event.timestamp)
                if deposit is not None:
                    deposits.append(deposit)
        return deposits

    def _advance_cursor(self, events: list[AccountEvent]) -> None:
        if not events:
            return
        newest = events[0]
        self._cursor = DepositCursorState(
            last_transaction_time=newest.timestamp - 1,
            last_transaction_id=self._event_transaction_id(newest),
        )
        self._cursor_store.save(self._cursor)

    async def poll_once(self) -> None:
        events = await self._ton_client.get_account_events(
            self._account_id, self._events_limit, self._cursor.last_transaction_time
        )
        deposits = self._extract_new_deposits(events)
        self._advance_cursor(events)
        for deposit in reversed(deposits):
            if not await self._deposit_repository.insert_deposit(deposit):
                logger.error("Failed to persist deposit %s", deposit.transaction_id)

    async def run(self) -> None:
        while True:
            try:
                await self.poll_once()
            except Exception:
                logger.exception("Deposit watcher iteration failed")
            await asyncio.sleep(self._poll_interval_seconds)
