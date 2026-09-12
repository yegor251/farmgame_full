import json
from pathlib import Path

from app.static_data import asset_lists
from app.static_data.models import (
    AmbarInfo,
    BakeryInfo,
    BushInfo,
    CorralInfo,
    DealInfo,
    GardenInfo,
    ItemInfo,
    MapInfo,
    ObstacleInfo,
    PlantInfo,
)


class StaticDataCatalog:
    def __init__(self, resources_dir: Path) -> None:
        self._resources_dir = resources_dir

        self.garden: GardenInfo = self._load(GardenInfo, resources_dir / "buildings" / "garden.json")
        self.ambar: AmbarInfo = self._load(AmbarInfo, resources_dir / "buildings" / "ambar.json")
        self.map: MapInfo = self._load(MapInfo, resources_dir / "map" / "map.json")

        self.bakeries: dict[str, BakeryInfo] = {
            name: self._load(BakeryInfo, resources_dir / "buildings" / f"{name}.json")
            for name in asset_lists.BAKERIES
        }
        self.corrals: dict[str, CorralInfo] = {
            name: self._load(CorralInfo, resources_dir / "buildings" / f"{name}.json")
            for name in asset_lists.CORRALS
        }
        self.bushes: dict[str, BushInfo] = {
            name: self._load(BushInfo, resources_dir / "buildings" / f"{name}.json")
            for name in asset_lists.BUSHES
        }
        self.obstacles: dict[str, ObstacleInfo] = {
            name: self._load(ObstacleInfo, resources_dir / "buildings" / "obstacles" / f"{name}.json")
            for name in asset_lists.OBSTACLES
        }
        self.plants: dict[str, PlantInfo] = {
            name: self._load(PlantInfo, resources_dir / "plants" / f"{name}.json")
            for name in asset_lists.SEEDS
        }
        self.items: dict[str, ItemInfo] = {
            name: self._load(ItemInfo, resources_dir / "items" / f"{name}.json")
            for name in asset_lists.ITEMS
        }
        self.deals: dict[str, DealInfo] = self._load_deals(resources_dir / "deals")

        self.building_type_by_name: dict[str, str] = (
            {name: "bakery" for name in self.bakeries}
            | {name: "corral" for name in self.corrals}
            | {name: "bush" for name in self.bushes}
            | {"garden": "garden"}
        )

    @staticmethod
    def _load[T](model: type[T], path: Path) -> T:
        data = json.loads(path.read_text(encoding="utf-8"))
        return model.model_validate(data)  # type: ignore[attr-defined,no-any-return]

    @classmethod
    def _load_deals(cls, deals_dir: Path) -> dict[str, DealInfo]:
        deals: dict[str, DealInfo] = {}
        for path in sorted(deals_dir.glob("*.json")):
            deal = cls._load(DealInfo, path)
            deals[deal.name] = deal
        return deals

    def building_exists(self, name: str) -> bool:
        return name in self.building_type_by_name

    def building_size(self, name: str) -> tuple[int, int]:
        building_type = self.building_type_by_name[name]
        if building_type == "garden":
            return (1, 1)
        building_info: BakeryInfo | CorralInfo | BushInfo
        if building_type == "bakery":
            building_info = self.bakeries[name]
        elif building_type == "corral":
            building_info = self.corrals[name]
        else:
            building_info = self.bushes[name]
        return (building_info.sizex, building_info.sizey)

    def building_map_limit(self, name: str) -> int:
        building_type = self.building_type_by_name[name]
        if building_type == "garden":
            return self.garden.map_limit
        if building_type == "bakery":
            return self.bakeries[name].map_limit
        if building_type == "corral":
            return self.corrals[name].map_limit
        return self.bushes[name].map_limit

    def building_price(self, name: str) -> int:
        building_type = self.building_type_by_name[name]
        if building_type == "garden":
            return self.garden.price
        if building_type == "bakery":
            return self.bakeries[name].price
        if building_type == "corral":
            return self.corrals[name].price
        return self.bushes[name].price

    def items_by_name_and_level(self, name: str, level: int) -> set[str]:
        building_type = self.building_type_by_name[name]
        if building_type == "garden":
            return set()
        if building_type == "corral":
            return set(self.corrals[name].products.keys())
        if building_type == "bush":
            return set(self.bushes[name].products.keys())
        bakery = self.bakeries[name]
        return {
            work_name
            for work_name, work_type in bakery.work_types.items()
            if work_type.min_level == level
        }

    def is_obstacle(self, name: str) -> bool:
        return name in self.obstacles

    def item_price(self, name: str) -> int:
        if name in self.items:
            return self.items[name].order_price
        if name in self.plants:
            return self.plants[name].order_price
        return 0

    def item_token_price(self, name: str) -> int:
        if name in self.items:
            return self.items[name].order_token_price
        if name in self.plants:
            return self.plants[name].order_token_price
        return 0

    def item_order_amount_limits(self, name: str) -> tuple[int, int]:
        item_info: ItemInfo | PlantInfo
        if name in self.items:
            item_info = self.items[name]
        elif name in self.plants:
            item_info = self.plants[name]
        else:
            return (0, 0)
        return (item_info.order_amount_min, item_info.order_amount_max)


_catalog: StaticDataCatalog | None = None


def load_catalog(resources_dir: Path) -> StaticDataCatalog:
    global _catalog
    _catalog = StaticDataCatalog(resources_dir)
    return _catalog


def get_catalog() -> StaticDataCatalog:
    if _catalog is None:
        raise RuntimeError("Static data catalog has not been loaded yet")
    return _catalog
