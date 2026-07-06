from typing import Any

from .._models.mock_image_embedding_provider import MockImageEmbeddingProvider
from .._settings import MockImageEmbeddingProviderSettings, settings_manager


def create_mock_image_embedding_provider(**kwargs: Any) -> MockImageEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockImageEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockImageEmbeddingProvider(settings)
