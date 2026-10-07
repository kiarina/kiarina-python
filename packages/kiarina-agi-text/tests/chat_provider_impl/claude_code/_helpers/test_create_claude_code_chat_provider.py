from kiarina.agi.chat_provider_impl.claude_code import (
    create_claude_code_chat_provider,
)


def test_create_claude_code_chat_provider() -> None:
    provider = create_claude_code_chat_provider(
        model_name="claude-opus-5-5", effort="low"
    )

    assert provider.settings.model_name == "claude-opus-5-5"
    assert str(provider) == "ClaudeCodeChatProvider(claude-opus-5-5, low)"
