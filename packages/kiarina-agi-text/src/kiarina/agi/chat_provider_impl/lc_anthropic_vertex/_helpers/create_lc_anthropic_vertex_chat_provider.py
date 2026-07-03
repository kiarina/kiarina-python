from typing import Any

from .._models.lc_anthropic_vertex_chat_provider import (
    LCAnthropicVertexChatProvider,
)
from .._settings import LCAnthropicVertexChatProviderSettings, settings_manager


def create_lc_anthropic_vertex_chat_provider(
    **kwargs: Any,
) -> LCAnthropicVertexChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = LCAnthropicVertexChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return LCAnthropicVertexChatProvider(settings)
