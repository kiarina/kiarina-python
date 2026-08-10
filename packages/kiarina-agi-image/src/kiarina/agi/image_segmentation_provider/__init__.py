from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.image_segmentation_provider_registry import (
        image_segmentation_provider_registry,
    )
    from ._models.base_image_segmentation_provider import BaseImageSegmentationProvider
    from ._settings import ImageSegmentationProviderSettings, settings_manager
    from ._types.image_segmentation_confidence_map import (
        ImageSegmentationConfidenceMap,
    )
    from ._types.image_segmentation_mask import ImageSegmentationMask
    from ._types.image_segmentation_provider import ImageSegmentationProvider
    from ._types.image_segmentation_provider_name import (
        ImageSegmentationProviderName,
    )
    from ._views.image_segmentation_result import ImageSegmentationResult

__all__ = [
    # ._instances
    "image_segmentation_provider_registry",
    # ._models
    "BaseImageSegmentationProvider",
    # ._settings
    "ImageSegmentationProviderSettings",
    "settings_manager",
    # ._types
    "ImageSegmentationConfidenceMap",
    "ImageSegmentationMask",
    "ImageSegmentationProvider",
    "ImageSegmentationProviderName",
    # ._views
    "ImageSegmentationResult",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        # ._instances
        "image_segmentation_provider_registry": "._instances.image_segmentation_provider_registry",
        # ._models
        "BaseImageSegmentationProvider": "._models.base_image_segmentation_provider",
        # ._settings
        "ImageSegmentationProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ImageSegmentationConfidenceMap": "._types.image_segmentation_confidence_map",
        "ImageSegmentationMask": "._types.image_segmentation_mask",
        "ImageSegmentationProvider": "._types.image_segmentation_provider",
        "ImageSegmentationProviderName": "._types.image_segmentation_provider_name",
        # ._views
        "ImageSegmentationResult": "._views.image_segmentation_result",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
