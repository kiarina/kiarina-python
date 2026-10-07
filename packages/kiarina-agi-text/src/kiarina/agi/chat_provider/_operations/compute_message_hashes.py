import hashlib
from typing import Any

from kiarina.agi.message import Message

from .compute_history_hash import compute_history_hash


def compute_message_hashes(messages: list[Message], **context: Any) -> list[str]:
    """
    A chained hash for each message: the hash of the history up to and including
    it, with `context` such as the model. Changing a message changes its hash
    and every later one, but not the earlier ones.

    A message counts by its type, text, tool calls, and tool result fields.
    Metadata does not count.
    """
    hashes: list[str] = []
    previous = compute_history_hash({"context": context})

    for message in messages:
        digest = compute_history_hash(_to_hashable(message))
        previous = hashlib.sha256(f"{previous}:{digest}".encode()).hexdigest()
        hashes.append(previous)

    return hashes


def _to_hashable(message: Message) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": message.type,
        "text": message.contents_to_text(),
    }

    if tool_calls := getattr(message, "tool_calls", None):
        value["tool_calls"] = [tool_call.model_dump() for tool_call in tool_calls]

    if message.type == "tool":
        value["tool_call_id"] = message.tool_call_id
        value["tool_name"] = message.tool_name
        value["failed"] = message.failed

    return value
