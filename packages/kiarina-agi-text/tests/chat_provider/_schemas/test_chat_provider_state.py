from kiarina.agi.chat_provider import CHAT_PROVIDER_STATE_KEY, ChatProviderState
from kiarina.agi.message import AIMessage


def test_chat_provider_state() -> None:
    message = AIMessage.create("Hi")
    assert ChatProviderState.from_message(message, "codex_app_server") is None

    state = ChatProviderState(
        name="codex_app_server", history_hash="h", data={"thread_id": "t"}
    )
    state.write_to(message)

    assert message.metadata[CHAT_PROVIDER_STATE_KEY] == {
        "name": "codex_app_server",
        "history_hash": "h",
        "data": {"thread_id": "t"},
    }
    assert ChatProviderState.from_message(message, "codex_app_server") == state
    assert ChatProviderState.from_message(message, "claude_agent_sdk") is None

    ChatProviderState(name="claude_agent_sdk", history_hash="h2").write_to(message)
    assert ChatProviderState.from_message(message, "codex_app_server") is None


def test_chat_provider_state_invalid() -> None:
    message = AIMessage.create("Hi")

    message.metadata[CHAT_PROVIDER_STATE_KEY] = "broken"
    assert ChatProviderState.from_message(message, "x") is None

    message.metadata[CHAT_PROVIDER_STATE_KEY] = {"name": "x"}
    assert ChatProviderState.from_message(message, "x") is None
