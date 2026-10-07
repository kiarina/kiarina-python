from typing import Any

from .._models.google_genai_chat_provider import GoogleGenAIChatProvider
from .._settings import GoogleGenAIChatProviderSettings, settings_manager


def create_google_genai_chat_provider(**kwargs: Any) -> GoogleGenAIChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleGenAIChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleGenAIChatProvider(settings)
