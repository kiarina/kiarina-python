from kiarina.agi.chat_provider_impl.openai import (
    OpenAIChatProvider,
    create_openai_chat_provider,
)


def test_create_openai_chat_provider() -> None:
    provider = create_openai_chat_provider(temperature=0.7)
    assert isinstance(provider, OpenAIChatProvider)
    assert provider.settings.temperature == 0.7


def test_create_openai_chat_provider_without_kwargs() -> None:
    provider = create_openai_chat_provider()
    assert provider.settings.endpoint_type == "chat_completions"
