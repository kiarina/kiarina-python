from typing import Any

from .._models.mock_image_segmentation_provider import MockImageSegmentationProvider
from .._settings import MockImageSegmentationProviderSettings, settings_manager


def create_mock_image_segmentation_provider(
    **kwargs: Any,
) -> MockImageSegmentationProvider:
    settings = settings_manager.get_settings()
    if kwargs:
        settings = MockImageSegmentationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )
    return MockImageSegmentationProvider(settings)
