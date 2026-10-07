from typing import Any

from .._models.codex_chat_provider import CodexChatProvider
from .._settings import CodexChatProviderSettings, settings_manager


def create_codex_chat_provider(
    **kwargs: Any,
) -> CodexChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = CodexChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return CodexChatProvider(settings)
