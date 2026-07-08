from typing import Any

from .._models.google_video_generation_provider import GoogleVideoGenerationProvider
from .._settings import GoogleVideoGenerationProviderSettings, settings_manager


def create_google_video_generation_provider(
    **kwargs: Any,
) -> GoogleVideoGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleVideoGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleVideoGenerationProvider(settings)
