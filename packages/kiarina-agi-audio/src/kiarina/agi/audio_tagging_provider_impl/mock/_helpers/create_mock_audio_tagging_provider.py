from typing import Any

from .._models.mock_audio_tagging_provider import MockAudioTaggingProvider
from .._settings import MockAudioTaggingProviderSettings, settings_manager


def create_mock_audio_tagging_provider(**kwargs: Any) -> MockAudioTaggingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockAudioTaggingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockAudioTaggingProvider(settings)
