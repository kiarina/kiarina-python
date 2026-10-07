from kiarina.agi.chat_provider_impl.codex_app_server import (
    create_codex_app_server_chat_provider,
)


def test_create_codex_app_server_chat_provider() -> None:
    provider = create_codex_app_server_chat_provider(reasoning_effort="medium")

    assert provider.settings.reasoning_effort == "medium"
    assert str(provider) == "CodexAppServerChatProvider(gpt-6.1-sol, medium)"
