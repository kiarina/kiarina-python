from kiarina.agi.chat_provider import compute_message_hashes
from kiarina.agi.message import AIMessage, HumanMessage, Message, ToolCall, ToolMessage


def _messages(first: str = "Hi") -> list[Message]:
    return [
        HumanMessage.create(first),
        AIMessage.create(tool_calls=[ToolCall(id="c", name="t")]),
        ToolMessage.create("ok", tool_name="t", tool_call_id="c"),
        AIMessage.create("Done"),
    ]


def test_compute_message_hashes() -> None:
    hashes = compute_message_hashes(_messages(), model_name="m")
    assert len(hashes) == 4
    assert len(set(hashes)) == 4

    # Metadata does not count.
    messages = _messages()
    messages[1].metadata["chat_provider"] = {"name": "x"}
    assert compute_message_hashes(messages, model_name="m") == hashes

    # A change moves its hash and every later one.
    edited = compute_message_hashes(_messages("Hello"), model_name="m")
    assert all(a != b for a, b in zip(edited, hashes, strict=True))

    messages = _messages()
    messages[2].failed = True  # type: ignore[union-attr]
    changed = compute_message_hashes(messages, model_name="m")
    assert changed[:2] == hashes[:2]
    assert changed[2:] != hashes[2:]

    # The context counts too.
    assert compute_message_hashes(_messages(), model_name="other")[0] != hashes[0]
