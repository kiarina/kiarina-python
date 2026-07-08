from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.audio_embedding_model import AudioEmbeddingModel
from .._schemas.audio_embedding_model_config import AudioEmbeddingModelConfig
from .._settings import settings_manager


def _configure(
    config: AudioEmbeddingModelConfig, values: dict[str, Any]
) -> AudioEmbeddingModelConfig:
    config.provider_config.update(values)
    return config


audio_embedding_model_registry = ObjectRegistry[
    AudioEmbeddingModel, AudioEmbeddingModelConfig
](
    expected_type=AudioEmbeddingModel,
    object_label="AudioEmbeddingModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: AudioEmbeddingModel(name, config),
)
