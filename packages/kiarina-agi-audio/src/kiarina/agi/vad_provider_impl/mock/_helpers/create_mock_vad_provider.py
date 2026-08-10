from typing import Any

from .._models.mock_vad_provider import MockVADProvider
from .._settings import MockVADProviderSettings, settings_manager


def create_mock_vad_provider(**kwargs: Any) -> MockVADProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockVADProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockVADProvider(settings)
