from typing import Any

from .._models.mock_asr_provider import MockASRProvider
from .._settings import MockASRProviderSettings, settings_manager


def create_mock_asr_provider(**kwargs: Any) -> MockASRProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockASRProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockASRProvider(settings)
