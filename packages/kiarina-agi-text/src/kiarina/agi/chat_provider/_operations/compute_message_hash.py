from typing import Any

from kiarina.agi.message import Message

from .compute_history_hash import compute_history_hash


def compute_message_hash(message: Message, **context: Any) -> str:
    """
    A hash of one message's text and tool calls, with `context` such as the
    model, for state tied to that message, such as its reasoning.
    """
    return compute_history_hash(
        {
            "type": message.type,
            "text": message.contents_to_text(),
            "tool_calls": [
                tool_call.model_dump()
                for tool_call in getattr(message, "tool_calls", [])
            ],
            "context": context,
        }
    )
