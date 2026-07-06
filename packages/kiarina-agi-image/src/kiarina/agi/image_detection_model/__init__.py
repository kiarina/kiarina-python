from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.crop_align_faces import crop_align_faces
    from ._helpers.crop_objects import crop_objects
    from ._helpers.detect_faces import detect_faces
    from ._helpers.detect_objects import detect_objects
    from ._models.image_detection_model import ImageDetectionModel
    from ._schemas.cropped_object import CroppedObject
    from ._schemas.image_detection_model_config import ImageDetectionModelConfig
    from ._services.image_detection_model_registry import (
        image_detection_model_registry,
    )
    from ._settings import ImageDetectionModelSettings, settings_manager
    from ._types.image_detection_model_alias import ImageDetectionModelAlias
    from ._types.image_detection_model_name import ImageDetectionModelName
    from ._types.image_detection_model_specifier import ImageDetectionModelSpecifier
    from ._types.image_detection_options import ImageDetectionOptions

__all__ = [
    "crop_align_faces",
    "crop_objects",
    "detect_faces",
    "detect_objects",
    "ImageDetectionModel",
    "CroppedObject",
    "ImageDetectionModelConfig",
    "image_detection_model_registry",
    "ImageDetectionModelSettings",
    "settings_manager",
    "ImageDetectionModelAlias",
    "ImageDetectionModelName",
    "ImageDetectionModelSpecifier",
    "ImageDetectionOptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "crop_align_faces": "._helpers.crop_align_faces",
        "crop_objects": "._helpers.crop_objects",
        "detect_faces": "._helpers.detect_faces",
        "detect_objects": "._helpers.detect_objects",
        "ImageDetectionModel": "._models.image_detection_model",
        "CroppedObject": "._schemas.cropped_object",
        "ImageDetectionModelConfig": "._schemas.image_detection_model_config",
        "image_detection_model_registry": "._services.image_detection_model_registry",
        "ImageDetectionModelSettings": "._settings",
        "settings_manager": "._settings",
        "ImageDetectionModelAlias": "._types.image_detection_model_alias",
        "ImageDetectionModelName": "._types.image_detection_model_name",
        "ImageDetectionModelSpecifier": "._types.image_detection_model_specifier",
        "ImageDetectionOptions": "._types.image_detection_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
