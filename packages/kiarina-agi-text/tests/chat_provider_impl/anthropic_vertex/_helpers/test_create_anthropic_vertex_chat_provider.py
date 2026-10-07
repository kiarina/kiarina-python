from kiarina.agi.chat_provider_impl.anthropic_vertex import (
    AnthropicVertexChatProvider,
    create_anthropic_vertex_chat_provider,
)


def test_create_anthropic_vertex_chat_provider() -> None:
    provider = create_anthropic_vertex_chat_provider(vertex_ai_location="global")
    assert isinstance(provider, AnthropicVertexChatProvider)
    assert provider.settings.vertex_ai_location == "global"


def test_create_anthropic_vertex_chat_provider_without_kwargs() -> None:
    provider = create_anthropic_vertex_chat_provider()
    assert provider.settings.token_count_model_name is None
