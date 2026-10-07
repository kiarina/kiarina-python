from typing import Any

from .._models.codex_app_server_chat_provider import CodexAppServerChatProvider
from .._settings import CodexAppServerChatProviderSettings, settings_manager


def create_codex_app_server_chat_provider(
    **kwargs: Any,
) -> CodexAppServerChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = CodexAppServerChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return CodexAppServerChatProvider(settings)
