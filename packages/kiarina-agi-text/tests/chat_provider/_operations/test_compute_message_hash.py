from kiarina.agi.chat_provider import compute_message_hash
from kiarina.agi.message import AIMessage, ToolCall


def test_compute_message_hash() -> None:
    message = AIMessage.create("Hi", tool_calls=[ToolCall(id="c", name="t")])
    a = compute_message_hash(message, model_name="m")

    # Metadata is not part of the hash.
    message.metadata["chat_provider"] = {"name": "x"}
    assert compute_message_hash(message, model_name="m") == a

    assert compute_message_hash(message, model_name="other") != a
    assert compute_message_hash(AIMessage.create("Hi"), model_name="m") != a
