from typing import Any

from .._models.mock_text_embedding_provider import MockTextEmbeddingProvider
from .._settings import MockTextEmbeddingProviderSettings, settings_manager


def create_mock_text_embedding_provider(**kwargs: Any) -> MockTextEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockTextEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockTextEmbeddingProvider(settings)
