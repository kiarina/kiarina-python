from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_gcs_asset_repository import create_gcs_asset_repository
    from ._services.gcs_asset_repository import GCSAssetRepository
    from ._settings import GCSAssetRepositorySettings, settings_manager

__all__ = [
    # ._helpers
    "create_gcs_asset_repository",
    # ._services
    "GCSAssetRepository",
    # ._settings
    "GCSAssetRepositorySettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_gcs_asset_repository": "._helpers.create_gcs_asset_repository",
        # ._services
        "GCSAssetRepository": "._services.gcs_asset_repository",
        # ._settings
        "GCSAssetRepositorySettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
