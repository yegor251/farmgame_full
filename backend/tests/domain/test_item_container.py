from app.domain.item_container import ItemContainer


def test_add_amount_within_capacity() -> None:
    container = ItemContainer()

    container.add_amount("wheat", 10)

    assert container.items["wheat"] == 10
    assert container.items_amount == 10


def test_add_amount_rejected_when_over_capacity() -> None:
    container = ItemContainer()
    container.capacity = 5

    container.add_amount("wheat", 10)

    assert container.items == {}
    assert container.items_amount == 0


def test_add_map_does_not_increment_amount_when_over_capacity() -> None:
    container = ItemContainer()
    container.capacity = 5

    container.add_map({"wheat": 3, "bread": 3})

    assert container.items == {}
    assert container.items_amount == 0


def test_add_map_adds_all_items_when_within_capacity() -> None:
    container = ItemContainer()

    container.add_map({"wheat": 3, "bread": 4})

    assert container.items == {"wheat": 3, "bread": 4}
    assert container.items_amount == 7


def test_enlarge_capacity_increases_limit() -> None:
    container = ItemContainer()

    container.enlarge_capacity(30)

    assert container.capacity == 100


def test_pull_random_returns_empty_list_when_no_items() -> None:
    container = ItemContainer()

    assert container.pull_random(3) == []


def test_pull_random_unique_returns_subset_of_known_keys() -> None:
    container = ItemContainer()
    container.add_amount("wheat", 1)
    container.add_amount("bread", 1)

    result = container.pull_random_unique(amount=2)

    assert result <= {"wheat", "bread"}
    assert len(result) == 2


def test_pull_random_unique_caps_at_available_keys() -> None:
    container = ItemContainer()
    container.add_amount("wheat", 1)

    result = container.pull_random_unique(amount=5)

    assert result == {"wheat"}
