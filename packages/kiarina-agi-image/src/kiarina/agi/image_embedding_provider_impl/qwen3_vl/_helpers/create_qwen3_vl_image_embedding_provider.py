from typing import Any

from .._models.qwen3_vl_image_embedding_provider import (
    Qwen3VLImageEmbeddingProvider,
)
from .._settings import Qwen3VLImageEmbeddingProviderSettings, settings_manager


def create_qwen3_vl_image_embedding_provider(
    **kwargs: Any,
) -> Qwen3VLImageEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = Qwen3VLImageEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return Qwen3VLImageEmbeddingProvider(settings)
