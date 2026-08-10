from typing import Any

from .._models.lc_anthropic_chat_provider import LCAnthropicChatProvider
from .._settings import LCAnthropicChatProviderSettings, settings_manager


def create_lc_anthropic_chat_provider(**kwargs: Any) -> LCAnthropicChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = LCAnthropicChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return LCAnthropicChatProvider(settings)
