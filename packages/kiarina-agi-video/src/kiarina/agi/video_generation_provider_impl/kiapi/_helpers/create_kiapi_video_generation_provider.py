from typing import Any

from .._models.kiapi_video_generation_provider import KiapiVideoGenerationProvider
from .._settings import KiapiVideoGenerationProviderSettings, settings_manager


def create_kiapi_video_generation_provider(
    **kwargs: Any,
) -> KiapiVideoGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = KiapiVideoGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return KiapiVideoGenerationProvider(settings)
