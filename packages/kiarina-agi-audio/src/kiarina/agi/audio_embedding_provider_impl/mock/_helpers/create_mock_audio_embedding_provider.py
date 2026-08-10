from typing import Any

from .._models.mock_audio_embedding_provider import MockAudioEmbeddingProvider
from .._settings import MockAudioEmbeddingProviderSettings, settings_manager


def create_mock_audio_embedding_provider(**kwargs: Any) -> MockAudioEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockAudioEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockAudioEmbeddingProvider(settings)
