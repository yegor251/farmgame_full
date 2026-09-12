from datetime import UTC, datetime, timedelta

from app.domain import boosters
from app.domain.boosters import ActiveBoosters, Booster, BoosterShelfEntry


def _booster(*, time: int, seconds_ago: int = 0) -> Booster:
    return Booster(
        booster_type="WorkSpeed",
        percentage=20,
        time=time,
        activate_timestamp=datetime.now(UTC) - timedelta(seconds=seconds_ago),
    )


def test_check_booster_true_before_expiry() -> None:
    assert boosters.check_booster(_booster(time=100, seconds_ago=10)) is True


def test_check_booster_false_after_expiry() -> None:
    assert boosters.check_booster(_booster(time=100, seconds_ago=200)) is False


def test_check_booster_false_when_none() -> None:
    assert boosters.check_booster(None) is False


def test_renew_booster_keeps_active_booster() -> None:
    booster = _booster(time=100, seconds_ago=10)

    assert boosters.renew_booster(booster) is booster


def test_renew_booster_drops_expired_booster() -> None:
    assert boosters.renew_booster(_booster(time=100, seconds_ago=200)) is None


def test_get_percentage_returns_zero_when_expired() -> None:
    assert boosters.get_percentage(_booster(time=100, seconds_ago=200)) == 0


def test_get_percentage_returns_value_when_active() -> None:
    assert boosters.get_percentage(_booster(time=100, seconds_ago=10)) == 20


def test_get_info_returns_zero_zero_when_expired() -> None:
    assert boosters.get_info(_booster(time=100, seconds_ago=200)) == (0, 0)


def test_get_info_returns_percentage_and_remaining_seconds() -> None:
    percentage, remaining = boosters.get_info(_booster(time=100, seconds_ago=10))

    assert percentage == 20
    assert 85 <= remaining <= 90


def test_regenerate_clears_expired_boosters_on_all_slots() -> None:
    active = ActiveBoosters()
    active.order_money = _booster(time=100, seconds_ago=200)
    active.work_speed = _booster(time=100, seconds_ago=10)

    boosters.regenerate(active)

    assert active.order_money is None
    assert active.work_speed is not None


def test_activate_sets_booster_on_matching_slot() -> None:
    active = ActiveBoosters()
    shelf_entry = BoosterShelfEntry(booster_type="GrowSpeed", percentage=15, time=3600)

    boosters.activate(active, shelf_entry)

    assert active.grow_speed is not None
    assert active.grow_speed.percentage == 15
    assert active.get("GrowSpeed") is active.grow_speed


def test_active_boosters_get_and_set_by_type_name() -> None:
    active = ActiveBoosters()
    booster = _booster(time=100)

    active.set("OrderItems", booster)

    assert active.get("OrderItems") is booster
    assert active.order_items is booster
