from typing import Protocol

from app.crypto.ton_api_models import AccountEvent


class EventsSource(Protocol):
    async def get_account_events(
        self, account_id: str, limit: int, start_date: int
    ) -> list[AccountEvent]: ...


class JettonWalletResolver(Protocol):
    async def get_jetton_wallet_address(self, account_id: str, jetton_id: str) -> str | None: ...


class TonNetworkClient(Protocol):
    async def get_seqno(self, address: str) -> int: ...

    async def send_boc(self, boc: str) -> None: ...


class JettonTransferSigner(Protocol):
    @property
    def address(self) -> str: ...

    def build_jetton_transfer_boc(
        self,
        jetton_wallet_address: str,
        to_address: str,
        jetton_amount: int,
        seqno: int,
        gas_ton: float,
    ) -> str: ...
