from app.domain.stats import Stats


def test_stats_initializes_zero_count_for_every_building_name() -> None:
    stats = Stats(["garden", "bakery"])

    assert stats.orders_completed == 0
    assert stats.buildings_placed == {"garden": 0, "bakery": 0}
