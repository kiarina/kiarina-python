from typing import Any

from .._models.google_asr_provider import GoogleASRProvider
from .._settings import GoogleASRProviderSettings, settings_manager


def create_google_asr_provider(**kwargs: Any) -> GoogleASRProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleASRProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleASRProvider(settings)
