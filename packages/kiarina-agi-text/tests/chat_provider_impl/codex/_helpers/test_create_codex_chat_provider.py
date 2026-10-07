from kiarina.agi.chat_provider_impl.codex import (
    create_codex_chat_provider,
)


def test_create_codex_chat_provider() -> None:
    provider = create_codex_chat_provider(reasoning_effort="medium")

    assert provider.settings.reasoning_effort == "medium"
    assert str(provider) == "CodexChatProvider(gpt-6.1-sol, medium)"
