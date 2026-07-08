from typing import Any

from .._models.openai_video_generation_provider import OpenAIVideoGenerationProvider
from .._settings import OpenAIVideoGenerationProviderSettings, settings_manager


def create_openai_video_generation_provider(
    **kwargs: Any,
) -> OpenAIVideoGenerationProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = OpenAIVideoGenerationProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return OpenAIVideoGenerationProvider(settings)
