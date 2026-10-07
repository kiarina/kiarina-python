from kiarina.agi.chat_provider_impl.anthropic import (
    AnthropicChatProvider,
    create_anthropic_chat_provider,
)


def test_create_anthropic_chat_provider() -> None:
    provider = create_anthropic_chat_provider(temperature=0.7)
    assert isinstance(provider, AnthropicChatProvider)
    assert provider.settings.temperature == 0.7


def test_create_anthropic_chat_provider_without_kwargs() -> None:
    provider = create_anthropic_chat_provider()
    assert provider.settings.cache_ttl == "5m"
