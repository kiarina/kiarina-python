from typing import TypeAlias

from .._models.ai_message_chunk_event import AIMessageChunkEvent
from .._models.ai_message_event import AIMessageEvent
from .._models.custom_event import CustomEvent
from .._models.human_message_event import HumanMessageEvent
from .._models.tool_message_event import ToolMessageEvent

Event: TypeAlias = (
    HumanMessageEvent
    | AIMessageEvent
    | AIMessageChunkEvent
    | ToolMessageEvent
    | CustomEvent
)
