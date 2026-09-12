import pytest

from app.domain.bakery import Bakery
from app.domain.building_factory import create_building
from app.domain.bush import Bush
from app.domain.corral import Corral
from app.domain.garden import Garden
from app.static_data.catalog import get_catalog


def test_create_building_returns_garden_for_garden_name() -> None:
    assert isinstance(create_building("garden"), Garden)


def test_create_building_returns_bakery_for_bakery_name() -> None:
    assert isinstance(create_building("bakery"), Bakery)


def test_create_building_returns_corral_for_corral_name() -> None:
    assert isinstance(create_building("coop"), Corral)


def test_create_building_returns_bush_with_catalog_speed_for_bush_name() -> None:
    bush = create_building("blackberry")

    assert isinstance(bush, Bush)
    assert bush.get_name() == "blackberry"
    assert (bush.ready_timestamp - bush.last_time_collected).total_seconds() == (
        get_catalog().bushes["blackberry"].speed
    )


def test_create_building_raises_for_unknown_name() -> None:
    with pytest.raises(KeyError):
        create_building("not_a_real_building")
