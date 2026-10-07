from typing import Any

from .._models.claude_code_chat_provider import ClaudeCodeChatProvider
from .._settings import ClaudeCodeChatProviderSettings, settings_manager


def create_claude_code_chat_provider(
    **kwargs: Any,
) -> ClaudeCodeChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = ClaudeCodeChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return ClaudeCodeChatProvider(settings)
