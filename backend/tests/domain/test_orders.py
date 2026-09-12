from datetime import UTC, datetime

from app.domain.orders import Order


def test_new_order_stores_fields_and_defaults_to_incomplete() -> None:
    start = datetime.now(UTC)

    order = Order({"bread": 2}, price=30, start_timestamp=start, token_price=5)

    assert order.items == {"bread": 2}
    assert order.price == 30
    assert order.token_price == 5
    assert order.start_timestamp == start
    assert order.completed is False
