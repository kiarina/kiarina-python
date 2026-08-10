from typing import Any

from .._models.mock_image_generation_provider import MockImageGenerationProvider
from .._settings import MockImageGenerationProviderSettings, settings_manager


def create_mock_image_generation_provider(**kwargs: Any) -> MockImageGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockImageGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockImageGenerationProvider(settings)
