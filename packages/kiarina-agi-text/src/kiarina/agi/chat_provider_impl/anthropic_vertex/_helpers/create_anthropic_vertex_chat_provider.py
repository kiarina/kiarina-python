from typing import Any

from .._models.anthropic_vertex_chat_provider import AnthropicVertexChatProvider
from .._settings import AnthropicVertexChatProviderSettings, settings_manager


def create_anthropic_vertex_chat_provider(**kwargs: Any) -> AnthropicVertexChatProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = AnthropicVertexChatProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return AnthropicVertexChatProvider(settings)
