from typing import Any

from .._models.google_image_generation_provider import GoogleImageGenerationProvider
from .._settings import GoogleImageGenerationProviderSettings, settings_manager


def create_google_image_generation_provider(
    **kwargs: Any,
) -> GoogleImageGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleImageGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleImageGenerationProvider(settings)
