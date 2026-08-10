from typing import Any

from .._models.openai_image_generation_provider import OpenAIImageGenerationProvider
from .._settings import OpenAIImageGenerationProviderSettings, settings_manager


def create_openai_image_generation_provider(
    **kwargs: Any,
) -> OpenAIImageGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = OpenAIImageGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return OpenAIImageGenerationProvider(settings)
