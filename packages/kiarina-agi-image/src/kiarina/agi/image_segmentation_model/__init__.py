from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.segment_image import segment_image
    from ._instances.image_segmentation_model_registry import (
        image_segmentation_model_registry,
    )
    from ._models.image_segmentation_model import ImageSegmentationModel
    from ._schemas.image_segmentation_model_config import ImageSegmentationModelConfig
    from ._settings import ImageSegmentationModelSettings, settings_manager
    from ._types.image_segmentation_model_alias import ImageSegmentationModelAlias
    from ._types.image_segmentation_model_name import ImageSegmentationModelName
    from ._types.image_segmentation_model_specifier import (
        ImageSegmentationModelSpecifier,
    )
    from ._types.image_segmentation_options import ImageSegmentationOptions

__all__ = [
    # ._helpers
    "segment_image",
    # ._instances
    "image_segmentation_model_registry",
    # ._models
    "ImageSegmentationModel",
    # ._schemas
    "ImageSegmentationModelConfig",
    # ._settings
    "ImageSegmentationModelSettings",
    "settings_manager",
    # ._types
    "ImageSegmentationModelAlias",
    "ImageSegmentationModelName",
    "ImageSegmentationModelSpecifier",
    "ImageSegmentationOptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_map = {
        # ._helpers
        "segment_image": "._helpers.segment_image",
        # ._instances
        "image_segmentation_model_registry": "._instances.image_segmentation_model_registry",
        # ._models
        "ImageSegmentationModel": "._models.image_segmentation_model",
        # ._schemas
        "ImageSegmentationModelConfig": "._schemas.image_segmentation_model_config",
        # ._settings
        "ImageSegmentationModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ImageSegmentationModelAlias": "._types.image_segmentation_model_alias",
        "ImageSegmentationModelName": "._types.image_segmentation_model_name",
        "ImageSegmentationModelSpecifier": "._types.image_segmentation_model_specifier",
        "ImageSegmentationOptions": "._types.image_segmentation_options",
    }
    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
