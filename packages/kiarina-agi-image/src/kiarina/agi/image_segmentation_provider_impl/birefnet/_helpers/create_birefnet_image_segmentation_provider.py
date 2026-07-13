from typing import Any

from .._models.birefnet_image_segmentation_provider import (
    BiRefNetImageSegmentationProvider,
)
from .._settings import BiRefNetImageSegmentationProviderSettings, settings_manager


def create_birefnet_image_segmentation_provider(
    **kwargs: Any,
) -> BiRefNetImageSegmentationProvider:
    settings = settings_manager.get_settings()
    if kwargs:
        settings = BiRefNetImageSegmentationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )
    return BiRefNetImageSegmentationProvider(settings)
