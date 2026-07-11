from typing import Any

from .._models.kiapi_image_generation_provider import KiapiImageGenerationProvider
from .._settings import KiapiImageGenerationProviderSettings, settings_manager


def create_kiapi_image_generation_provider(
    **kwargs: Any,
) -> KiapiImageGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = KiapiImageGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return KiapiImageGenerationProvider(settings)
