from typing import Any

from .._models.openai_chat_provider import OpenAIChatProvider
from .._settings import OpenAIChatProviderSettings, settings_manager


def create_openai_chat_provider(**kwargs: Any) -> OpenAIChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = OpenAIChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return OpenAIChatProvider(settings)
