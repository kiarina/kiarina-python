from typing import Any

from .._models.openai_tts_provider import OpenAITTSProvider
from .._settings import OpenAITTSProviderSettings, settings_manager


def create_openai_tts_provider(**kwargs: Any) -> OpenAITTSProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = OpenAITTSProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return OpenAITTSProvider(settings)
