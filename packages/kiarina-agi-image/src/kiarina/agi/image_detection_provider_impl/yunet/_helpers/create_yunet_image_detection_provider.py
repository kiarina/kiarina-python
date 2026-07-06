from typing import Any

from .._models.yunet_image_detection_provider import YuNetImageDetectionProvider
from .._settings import YuNetImageDetectionProviderSettings, settings_manager


def create_yunet_image_detection_provider(**kwargs: Any) -> YuNetImageDetectionProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = YuNetImageDetectionProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return YuNetImageDetectionProvider(settings)
