from typing import Any

from .._models.rapidocr_provider import RapidOCRProvider
from .._settings import RapidOCRProviderSettings, settings_manager


def create_rapidocr_provider(**kwargs: Any) -> RapidOCRProvider:
    settings = settings_manager.get_settings()
    if kwargs:
        settings = RapidOCRProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )
    return RapidOCRProvider(settings)
