from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._services.local_asset_repository import LocalAssetRepository

__all__ = [
    # ._services
    "LocalAssetRepository",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._services
        "LocalAssetRepository": "._services.local_asset_repository",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
