import pytest

from app.config import settings
from app.static_data.catalog import load_catalog


@pytest.fixture(scope="session", autouse=True)
def _load_static_catalog() -> None:
    load_catalog(settings.resources_dir)
