from kiarina.agi.chat_provider_impl.google_genai import (
    GoogleGenAIChatProvider,
    create_google_genai_chat_provider,
)


def test_create_google_genai_chat_provider() -> None:
    provider = create_google_genai_chat_provider(temperature=0.7)
    assert isinstance(provider, GoogleGenAIChatProvider)
    assert provider.settings.temperature == 0.7


def test_create_google_genai_chat_provider_without_kwargs() -> None:
    provider = create_google_genai_chat_provider()
    assert provider.settings.parallel_tool_calls is False
