from app.domain.bakery import Bakery
from app.domain.buildable import Buildable
from app.domain.bush import Bush
from app.domain.corral import Corral
from app.domain.garden import Garden
from app.static_data.catalog import get_catalog


def create_building(name: str) -> Buildable:
    catalog = get_catalog()
    building_type = catalog.building_type_by_name[name]
    if building_type == "bakery":
        return Bakery(name)
    if building_type == "garden":
        return Garden()
    if building_type == "corral":
        return Corral(name)
    if building_type == "bush":
        return Bush(name, catalog.bushes[name].speed)
    raise ValueError(f"Unknown building type for {name!r}")
