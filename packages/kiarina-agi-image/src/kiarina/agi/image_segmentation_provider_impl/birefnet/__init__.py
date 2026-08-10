from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_birefnet_image_segmentation_provider import (
        create_birefnet_image_segmentation_provider,
    )
    from ._models.birefnet_image_segmentation_provider import (
        BiRefNetImageSegmentationProvider,
    )
    from ._settings import BiRefNetImageSegmentationProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_birefnet_image_segmentation_provider",
    # ._models
    "BiRefNetImageSegmentationProvider",
    # ._settings
    "BiRefNetImageSegmentationProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        # ._helpers
        "create_birefnet_image_segmentation_provider": "._helpers.create_birefnet_image_segmentation_provider",
        # ._models
        "BiRefNetImageSegmentationProvider": "._models.birefnet_image_segmentation_provider",
        # ._settings
        "BiRefNetImageSegmentationProviderSettings": "._settings",
        "settings_manager": "._settings",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
