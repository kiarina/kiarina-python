from kiarina.agi.chat_provider_impl.google import (
    GoogleChatProvider,
    create_google_chat_provider,
)


def test_create_google_chat_provider() -> None:
    provider = create_google_chat_provider(temperature=0.7)
    assert isinstance(provider, GoogleChatProvider)
    assert provider.settings.temperature == 0.7


def test_create_google_chat_provider_without_kwargs() -> None:
    provider = create_google_chat_provider()
    assert provider.settings.parallel_tool_calls is False
