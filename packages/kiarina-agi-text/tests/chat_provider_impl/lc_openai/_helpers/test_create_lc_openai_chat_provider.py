# mypy: ignore-errors

from kiarina.agi.chat_provider_impl.lc_openai import (
    LCOpenAIChatProvider,
    create_lc_openai_chat_provider,
)


def test_create_lc_openai_chat_provider():
    provider = create_lc_openai_chat_provider(temperature=0.7)
    assert isinstance(provider, LCOpenAIChatProvider)
    assert provider.settings.temperature == 0.7
