from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_asset_cache import create_asset_cache
    from ._services.asset_cache import AssetCache
    from ._settings import AssetCacheSettings, settings_manager

__all__ = [
    # ._helpers
    "create_asset_cache",
    # ._services
    "AssetCache",
    # ._settings
    "AssetCacheSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_asset_cache": "._helpers.create_asset_cache",
        # ._services
        "AssetCache": "._services.asset_cache",
        # ._settings
        "AssetCacheSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
