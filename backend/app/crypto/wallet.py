from tonsdk.contract.token.ft import JettonWallet
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import Address, bytes_to_b64str, to_nano


class HotWallet:
    def __init__(self, mnemonic: str, workchain: int = 0) -> None:
        _, _, _, wallet = Wallets.from_mnemonics(mnemonic.split(), WalletVersionEnum.v4r2, workchain)
        self._wallet = wallet

    @property
    def address(self) -> str:
        return str(self._wallet.address.to_string(True, True, False))

    def build_jetton_transfer_boc(
        self,
        jetton_wallet_address: str,
        to_address: str,
        jetton_amount: int,
        seqno: int,
        gas_ton: float,
    ) -> str:
        transfer_body = JettonWallet().create_transfer_body(
            to_address=Address(to_address),
            jetton_amount=jetton_amount,
            response_address=self._wallet.address,
        )
        query = self._wallet.create_transfer_message(
            to_addr=jetton_wallet_address,
            amount=to_nano(gas_ton, "ton"),
            seqno=seqno,
            payload=transfer_body,
        )
        return str(bytes_to_b64str(query["message"].to_boc(False)))
