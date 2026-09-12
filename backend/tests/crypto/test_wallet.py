from tonsdk.contract.wallet import mnemonic_new

from app.crypto.wallet import HotWallet


def _wallet() -> HotWallet:
    return HotWallet(" ".join(mnemonic_new()))


def test_address_is_stable_across_instances_from_same_mnemonic() -> None:
    mnemonic = " ".join(mnemonic_new())

    assert HotWallet(mnemonic).address == HotWallet(mnemonic).address


def test_build_jetton_transfer_boc_returns_base64_payload() -> None:
    wallet = _wallet()

    boc = wallet.build_jetton_transfer_boc(
        jetton_wallet_address=wallet.address,
        to_address=wallet.address,
        jetton_amount=1000,
        seqno=0,
        gas_ton=0.05,
    )

    assert isinstance(boc, str)
    assert len(boc) > 0
