from typing import Any

from .._models.dfine_image_detection_provider import DFineImageDetectionProvider
from .._settings import DFineImageDetectionProviderSettings, settings_manager


def create_dfine_image_detection_provider(**kwargs: Any) -> DFineImageDetectionProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = DFineImageDetectionProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return DFineImageDetectionProvider(settings)
