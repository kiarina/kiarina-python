from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.image_embedding_model import ImageEmbeddingModel
from .._schemas.image_embedding_model_config import ImageEmbeddingModelConfig
from .._settings import settings_manager


def _configure(
    config: ImageEmbeddingModelConfig, values: dict[str, Any]
) -> ImageEmbeddingModelConfig:
    config.provider_config.update(values)
    return config


image_embedding_model_registry = ObjectRegistry[
    ImageEmbeddingModel, ImageEmbeddingModelConfig
](
    expected_type=ImageEmbeddingModel,
    object_label="ImageEmbeddingModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: ImageEmbeddingModel(name, config),
)
