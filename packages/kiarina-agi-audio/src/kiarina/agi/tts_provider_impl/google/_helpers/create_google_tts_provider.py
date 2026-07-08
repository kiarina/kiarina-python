from typing import Any

from .._models.google_tts_provider import GoogleTTSProvider
from .._settings import GoogleTTSProviderSettings, settings_manager


def create_google_tts_provider(**kwargs: Any) -> GoogleTTSProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleTTSProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleTTSProvider(settings)
