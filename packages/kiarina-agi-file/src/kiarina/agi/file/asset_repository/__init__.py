from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_asset_repository import create_asset_repository
    from ._instances.asset_repository_registry import asset_repository_registry
    from ._models.base_asset_repository import BaseAssetRepository
    from ._schemas.uri_policy import URIPolicy
    from ._settings import AssetRepositorySettings, settings_manager
    from ._types.asset_area import AssetArea
    from ._types.asset_repository import AssetRepository
    from ._types.asset_repository_name import AssetRepositoryName
    from ._types.asset_repository_specifier import AssetRepositorySpecifier
    from ._types.cached_file_blob import CachedFileBlob

__all__ = [
    # ._helpers
    "create_asset_repository",
    # ._instances
    "asset_repository_registry",
    # ._models
    "BaseAssetRepository",
    # ._schemas
    "URIPolicy",
    # ._settings
    "AssetRepositorySettings",
    "settings_manager",
    # ._types
    "AssetArea",
    "AssetRepositoryName",
    "AssetRepositorySpecifier",
    "AssetRepository",
    "CachedFileBlob",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_asset_repository": "._helpers.create_asset_repository",
        # ._instances
        "asset_repository_registry": "._instances.asset_repository_registry",
        # ._models
        "BaseAssetRepository": "._models.base_asset_repository",
        # ._schemas
        "URIPolicy": "._schemas.uri_policy",
        # ._settings
        "AssetRepositorySettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "AssetArea": "._types.asset_area",
        "AssetRepositoryName": "._types.asset_repository_name",
        "AssetRepositorySpecifier": "._types.asset_repository_specifier",
        "AssetRepository": "._types.asset_repository",
        "CachedFileBlob": "._types.cached_file_blob",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
