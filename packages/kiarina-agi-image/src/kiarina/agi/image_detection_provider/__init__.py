from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.image_detection_provider_registry import (
        image_detection_provider_registry,
    )
    from ._models.base_image_detection_provider import BaseImageDetectionProvider
    from ._settings import ImageDetectionProviderSettings, settings_manager
    from ._types.image_detection_provider import ImageDetectionProvider
    from ._types.image_detection_provider_name import ImageDetectionProviderName
    from ._types.keypoint_type import KeypointType
    from ._views.detected_object import DetectedObject

__all__ = [
    # ._instances
    "image_detection_provider_registry",
    # ._models
    "BaseImageDetectionProvider",
    # ._settings
    "ImageDetectionProviderSettings",
    "settings_manager",
    # ._types
    "ImageDetectionProvider",
    "ImageDetectionProviderName",
    "KeypointType",
    # ._views
    "DetectedObject",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._instances
        "image_detection_provider_registry": "._instances.image_detection_provider_registry",
        # ._models
        "BaseImageDetectionProvider": "._models.base_image_detection_provider",
        # ._settings
        "ImageDetectionProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ImageDetectionProvider": "._types.image_detection_provider",
        "ImageDetectionProviderName": "._types.image_detection_provider_name",
        "KeypointType": "._types.keypoint_type",
        # ._views
        "DetectedObject": "._views.detected_object",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
