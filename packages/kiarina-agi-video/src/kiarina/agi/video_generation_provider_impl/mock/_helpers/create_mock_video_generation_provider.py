from typing import Any

from .._models.mock_video_generation_provider import MockVideoGenerationProvider
from .._settings import MockVideoGenerationProviderSettings, settings_manager


def create_mock_video_generation_provider(**kwargs: Any) -> MockVideoGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockVideoGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockVideoGenerationProvider(settings)
