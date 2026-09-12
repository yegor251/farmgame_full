from app.domain.wallet import Wallet


def test_new_wallet_starts_at_zero_balances() -> None:
    wallet = Wallet()

    assert wallet.token_balance == 0
    assert wallet.usdt_balance == 0
    assert wallet.ton_balance == 0
