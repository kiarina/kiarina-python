from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.image_generation_model import ImageGenerationModel
from .._schemas.image_generation_model_config import ImageGenerationModelConfig
from .._settings import settings_manager


def _configure(
    config: ImageGenerationModelConfig, values: dict[str, Any]
) -> ImageGenerationModelConfig:
    config.provider_config.update(values)
    return config


image_generation_model_registry = ObjectRegistry[
    ImageGenerationModel, ImageGenerationModelConfig
](
    expected_type=ImageGenerationModel,
    object_label="ImageGenerationModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: ImageGenerationModel(name, config),
)
