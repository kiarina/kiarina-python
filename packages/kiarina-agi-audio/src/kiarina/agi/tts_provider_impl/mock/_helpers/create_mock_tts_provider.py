from typing import Any

from .._models.mock_tts_provider import MockTTSProvider
from .._settings import MockTTSProviderSettings, settings_manager


def create_mock_tts_provider(**kwargs: Any) -> MockTTSProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockTTSProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockTTSProvider(settings)
