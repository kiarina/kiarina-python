from typing import Any

from .._models.gemini_image_embedding_provider import GeminiImageEmbeddingProvider
from .._settings import GeminiImageEmbeddingProviderSettings, settings_manager


def create_gemini_image_embedding_provider(
    **kwargs: Any,
) -> GeminiImageEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GeminiImageEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GeminiImageEmbeddingProvider(settings)
