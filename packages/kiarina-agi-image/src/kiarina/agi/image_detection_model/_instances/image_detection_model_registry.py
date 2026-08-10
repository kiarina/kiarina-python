from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.image_detection_model import ImageDetectionModel
from .._schemas.image_detection_model_config import ImageDetectionModelConfig
from .._settings import settings_manager


def _configure(
    config: ImageDetectionModelConfig, values: dict[str, Any]
) -> ImageDetectionModelConfig:
    config.provider_config.update(values)
    return config


image_detection_model_registry = ObjectRegistry[
    ImageDetectionModel, ImageDetectionModelConfig
](
    expected_type=ImageDetectionModel,
    object_label="ImageDetectionModel",
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: ImageDetectionModel(name, config),
)
