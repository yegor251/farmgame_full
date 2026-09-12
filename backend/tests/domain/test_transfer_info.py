from app.domain.transfer_info import Deposit, TransferInfo, Withdraw


def test_new_transfer_info_starts_with_empty_lists() -> None:
    transfer_info = TransferInfo()

    assert transfer_info.deposits == []
    assert transfer_info.withdraws == []


def test_deposit_stores_all_fields() -> None:
    deposit = Deposit(
        transaction_id=1,
        active=True,
        tg_id=42,
        amount=1000,
        time_stamp=123,
        jetton_signature="sig",
        commentary="note",
    )

    assert deposit.transaction_id == 1
    assert deposit.active is True
    assert deposit.tg_id == 42
    assert deposit.amount == 1000
    assert deposit.time_stamp == 123
    assert deposit.jetton_signature == "sig"
    assert deposit.commentary == "note"


def test_withdraw_stores_all_fields() -> None:
    withdraw = Withdraw(transaction_id=2, status=0, tg_id=42, wallet="EQ...", amount=500, time_stamp=456)

    assert withdraw.transaction_id == 2
    assert withdraw.status == 0
    assert withdraw.tg_id == 42
    assert withdraw.wallet == "EQ..."
    assert withdraw.amount == 500
    assert withdraw.time_stamp == 456
