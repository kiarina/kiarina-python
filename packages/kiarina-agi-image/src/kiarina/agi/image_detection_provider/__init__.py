from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.base_image_detection_provider import BaseImageDetectionProvider
    from ._schemas.detected_object import DetectedObject
    from ._services.image_detection_provider_registry import (
        image_detection_provider_registry,
    )
    from ._settings import ImageDetectionProviderSettings, settings_manager
    from ._types.image_detection_provider import ImageDetectionProvider
    from ._types.image_detection_provider_name import ImageDetectionProviderName
    from ._types.keypoint_type import KeypointType

__all__ = [
    "BaseImageDetectionProvider",
    "DetectedObject",
    "image_detection_provider_registry",
    "ImageDetectionProviderSettings",
    "settings_manager",
    "ImageDetectionProvider",
    "ImageDetectionProviderName",
    "KeypointType",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "BaseImageDetectionProvider": "._models.base_image_detection_provider",
        "DetectedObject": "._schemas.detected_object",
        "image_detection_provider_registry": "._services.image_detection_provider_registry",
        "ImageDetectionProviderSettings": "._settings",
        "settings_manager": "._settings",
        "ImageDetectionProvider": "._types.image_detection_provider",
        "ImageDetectionProviderName": "._types.image_detection_provider_name",
        "KeypointType": "._types.keypoint_type",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
