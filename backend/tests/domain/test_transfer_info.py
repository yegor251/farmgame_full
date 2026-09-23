from app.domain.transfer_info import Deposit, TransferInfo


def test_new_transfer_info_starts_with_empty_lists() -> None:
    transfer_info = TransferInfo()

    assert transfer_info.deposits == []


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
