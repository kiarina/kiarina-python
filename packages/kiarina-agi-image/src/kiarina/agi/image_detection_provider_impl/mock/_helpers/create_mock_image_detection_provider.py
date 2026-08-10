from typing import Any

from .._models.mock_image_detection_provider import MockImageDetectionProvider
from .._settings import MockImageDetectionProviderSettings, settings_manager


def create_mock_image_detection_provider(**kwargs: Any) -> MockImageDetectionProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockImageDetectionProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MockImageDetectionProvider(settings)
