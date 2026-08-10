from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.text_embedding_model import TextEmbeddingModel
from .._schemas.text_embedding_model_config import TextEmbeddingModelConfig
from .._settings import settings_manager


def _configure(
    config: TextEmbeddingModelConfig, values: dict[str, Any]
) -> TextEmbeddingModelConfig:
    config.provider_config.update(values)
    return config


text_embedding_model_registry = ObjectRegistry[
    TextEmbeddingModel, TextEmbeddingModelConfig
](
    expected_type=TextEmbeddingModel,
    object_label="TextEmbeddingModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: TextEmbeddingModel(name, config),
)
