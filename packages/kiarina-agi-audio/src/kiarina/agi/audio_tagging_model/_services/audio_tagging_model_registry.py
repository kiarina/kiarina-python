from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.audio_tagging_model import AudioTaggingModel
from .._schemas.audio_tagging_model_config import AudioTaggingModelConfig
from .._settings import settings_manager


def _configure(
    config: AudioTaggingModelConfig, values: dict[str, Any]
) -> AudioTaggingModelConfig:
    config.provider_config.update(values)
    return config


audio_tagging_model_registry = ObjectRegistry[
    AudioTaggingModel, AudioTaggingModelConfig
](
    expected_type=AudioTaggingModel,
    object_label="AudioTaggingModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: AudioTaggingModel(name, config),
)
