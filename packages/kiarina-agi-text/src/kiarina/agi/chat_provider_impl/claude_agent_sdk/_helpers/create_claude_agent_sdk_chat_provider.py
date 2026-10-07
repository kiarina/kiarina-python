from typing import Any

from .._models.claude_agent_sdk_chat_provider import ClaudeAgentSDKChatProvider
from .._settings import ClaudeAgentSDKChatProviderSettings, settings_manager


def create_claude_agent_sdk_chat_provider(
    **kwargs: Any,
) -> ClaudeAgentSDKChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = ClaudeAgentSDKChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return ClaudeAgentSDKChatProvider(settings)
