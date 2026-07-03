from typing import Any

from .._models.openai_text_embedding_provider import OpenAITextEmbeddingProvider
from .._settings import OpenAITextEmbeddingProviderSettings, settings_manager


def create_openai_text_embedding_provider(
    **kwargs: Any,
) -> OpenAITextEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = OpenAITextEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return OpenAITextEmbeddingProvider(settings)
