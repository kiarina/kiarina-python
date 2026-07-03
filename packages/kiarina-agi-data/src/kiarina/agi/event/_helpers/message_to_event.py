from kiarina.agi.message import AIMessageChunk, Message

from .._models.ai_message_chunk_event import AIMessageChunkEvent
from .._models.ai_message_event import AIMessageEvent
from .._models.human_message_event import HumanMessageEvent
from .._models.tool_message_event import ToolMessageEvent
from .._types.event import Event


def message_to_event(message: Message) -> Event:
    if isinstance(message, AIMessageChunk):
        return AIMessageChunkEvent(message=message)
    elif message.type == "human":
        return HumanMessageEvent(message=message)
    elif message.type == "ai":
        return AIMessageEvent(message=message)
    elif message.type == "tool":
        return ToolMessageEvent(message=message)
    else:  # pragma: no cover
        raise AssertionError(f"Unsupported message type: {message.type}")
