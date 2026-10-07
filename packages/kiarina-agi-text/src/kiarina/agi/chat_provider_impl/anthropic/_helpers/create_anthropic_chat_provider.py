from typing import Any

from .._models.anthropic_chat_provider import AnthropicChatProvider
from .._settings import AnthropicChatProviderSettings, settings_manager


def create_anthropic_chat_provider(**kwargs: Any) -> AnthropicChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = AnthropicChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return AnthropicChatProvider(settings)
