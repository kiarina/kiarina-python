from typing import Any

from .._models.google_text_embedding_provider import GoogleTextEmbeddingProvider
from .._settings import GoogleTextEmbeddingProviderSettings, settings_manager


def create_google_text_embedding_provider(
    **kwargs: Any,
) -> GoogleTextEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleTextEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleTextEmbeddingProvider(settings)
