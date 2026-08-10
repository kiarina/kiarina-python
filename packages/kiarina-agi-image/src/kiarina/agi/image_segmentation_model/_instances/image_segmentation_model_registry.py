from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.image_segmentation_model import ImageSegmentationModel
from .._schemas.image_segmentation_model_config import ImageSegmentationModelConfig
from .._settings import settings_manager


def _configure(
    config: ImageSegmentationModelConfig, values: dict[str, Any]
) -> ImageSegmentationModelConfig:
    config.provider_config.update(values)
    return config


image_segmentation_model_registry = ObjectRegistry[
    ImageSegmentationModel, ImageSegmentationModelConfig
](
    expected_type=ImageSegmentationModel,
    object_label="ImageSegmentationModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: ImageSegmentationModel(name, config),
)
