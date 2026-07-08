from typing import Any

from .._models.openai_asr_provider import OpenAIASRProvider
from .._settings import OpenAIASRProviderSettings, settings_manager


def create_openai_asr_provider(**kwargs: Any) -> OpenAIASRProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = OpenAIASRProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return OpenAIASRProvider(settings)
