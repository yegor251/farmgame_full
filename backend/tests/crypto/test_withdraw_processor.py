from app.crypto.withdraw_processor import WithdrawProcessor
from app.domain.transfer_info import Withdraw

WALLET_ADDRESS = "UQ_hot_wallet"
JETTON_MASTER_ADDRESS = "0:master"
JETTON_WALLET_ADDRESS = "0:jetton-wallet"


class _FakeWallet:
    def __init__(self) -> None:
        self.address = WALLET_ADDRESS
        self.built_bocs: list[tuple[str, str, int, int]] = []

    def build_jetton_transfer_boc(
        self,
        jetton_wallet_address: str,
        to_address: str,
        jetton_amount: int,
        seqno: int,
        gas_ton: float,
    ) -> str:
        self.built_bocs.append((jetton_wallet_address, to_address, jetton_amount, seqno))
        return "boc"


class _FakeJettonWalletResolver:
    def __init__(self, address: str | None) -> None:
        self._address = address
        self.calls = 0

    async def get_jetton_wallet_address(self, account_id: str, jetton_id: str) -> str | None:
        self.calls += 1
        return self._address


class _FakeToncenterClient:
    def __init__(self, seqno_sequence: list[int]) -> None:
        self._seqno_sequence = seqno_sequence
        self.sent_bocs: list[str] = []

    async def get_seqno(self, address: str) -> int:
        if len(self._seqno_sequence) > 1:
            return self._seqno_sequence.pop(0)
        return self._seqno_sequence[0]

    async def send_boc(self, boc: str) -> None:
        self.sent_bocs.append(boc)


def _processor(
    wallet: _FakeWallet, toncenter: _FakeToncenterClient, resolver: _FakeJettonWalletResolver
) -> WithdrawProcessor:
    return WithdrawProcessor(
        wallet=wallet,  # type: ignore[arg-type]
        toncenter_client=toncenter,  # type: ignore[arg-type]
        jetton_wallet_resolver=resolver,  # type: ignore[arg-type]
        withdraw_repository=None,  # type: ignore[arg-type]
        jetton_master_address=JETTON_MASTER_ADDRESS,
        gas_ton=0.05,
        batch_limit=100,
        retry_interval_seconds=0,
        idle_sleep_seconds=0,
    )


async def test_resolve_jetton_wallet_address_caches_result() -> None:
    resolver = _FakeJettonWalletResolver(JETTON_WALLET_ADDRESS)
    processor = _processor(_FakeWallet(), _FakeToncenterClient([0]), resolver)

    first = await processor._resolve_jetton_wallet_address()
    second = await processor._resolve_jetton_wallet_address()

    assert first == second == JETTON_WALLET_ADDRESS
    assert resolver.calls == 1


async def test_send_until_confirmed_resends_until_seqno_advances() -> None:
    wallet = _FakeWallet()
    toncenter = _FakeToncenterClient([3, 3, 3, 4])
    processor = _processor(wallet, toncenter, _FakeJettonWalletResolver(JETTON_WALLET_ADDRESS))
    withdraw = Withdraw(
        transaction_id=1, status=1, tg_id=7, wallet="EQdest", amount=1000, time_stamp=0
    )

    await processor._send_until_confirmed(withdraw, JETTON_WALLET_ADDRESS)

    assert len(toncenter.sent_bocs) == 2
    assert all(entry[3] == 3 for entry in wallet.built_bocs)
