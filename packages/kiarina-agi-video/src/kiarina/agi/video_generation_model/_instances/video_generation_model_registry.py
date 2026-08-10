from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.video_generation_model import VideoGenerationModel
from .._schemas.video_generation_model_config import VideoGenerationModelConfig
from .._settings import settings_manager


def _configure(
    config: VideoGenerationModelConfig, values: dict[str, Any]
) -> VideoGenerationModelConfig:
    config.provider_config.update(values)
    return config


video_generation_model_registry = ObjectRegistry[
    VideoGenerationModel, VideoGenerationModelConfig
](
    expected_type=VideoGenerationModel,
    object_label="VideoGenerationModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: VideoGenerationModel(name, config),
)
