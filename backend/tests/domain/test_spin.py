from app.domain.spin import Spin


def test_new_spin_stores_items_and_drop_and_starts_unactivated() -> None:
    items = [("money", 10), ("wheat", 1)]

    spin = Spin(items, ("wheat", 2))

    assert spin.items == items
    assert spin.drop == ("wheat", 2)
    assert spin.activated is False
