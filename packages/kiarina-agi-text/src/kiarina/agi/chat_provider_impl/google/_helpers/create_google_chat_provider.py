from typing import Any

from .._models.google_chat_provider import GoogleChatProvider
from .._settings import GoogleChatProviderSettings, settings_manager


def create_google_chat_provider(**kwargs: Any) -> GoogleChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GoogleChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GoogleChatProvider(settings)
