from app.domain.deals import Deals


def test_new_deals_start_empty() -> None:
    deals = Deals()

    assert deals.bought_deals == set()
    assert deals.token_spent == 0
    assert deals.usdt_spent == 0
    assert deals.ton_spent == 0
    assert deals.boosters == []
