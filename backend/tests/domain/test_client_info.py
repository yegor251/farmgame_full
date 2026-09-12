from app.domain.client_info import ClientInfo


def test_new_client_info_has_expected_defaults() -> None:
    client_info = ClientInfo(tg_id=42, ref_id=7)

    assert client_info.tg_id == 42
    assert client_info.ref_id == 7
    assert client_info.wallet == "no"
    assert client_info.banned is False
    assert client_info.strikes == 0
    assert client_info.referrals == []
