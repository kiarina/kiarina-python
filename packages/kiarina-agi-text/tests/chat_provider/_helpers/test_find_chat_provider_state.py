from kiarina.agi.chat_provider import ChatProviderState, find_chat_provider_state
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolMessage,
)


def _ai(name: str | None) -> AIMessage:
    message = AIMessage.create(tool_calls=[ToolCall(id="c", name="t")])

    if name:
        ChatProviderState(name=name, history_hash="h").write_to(message)

    return message


def test_find_chat_provider_state() -> None:
    messages: list[Message] = [
        HumanMessage.create("Hi"),
        _ai("codex"),
        ToolMessage.create("ok", tool_name="t", tool_call_id="c"),
    ]

    found = find_chat_provider_state(messages, "codex")
    assert found is not None
    assert found[0] == 1
    assert found[1].history_hash == "h"

    assert find_chat_provider_state(messages, "claude_code") is None
    assert find_chat_provider_state(messages[:1], "codex") is None

    # A later AI message without the state hides the older one.
    assert find_chat_provider_state([*messages, _ai(None)], "codex") is None
