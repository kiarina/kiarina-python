from typing import TypeAlias

from .._models.ai_message import AIMessage
from .._models.ai_message_chunk import AIMessageChunk
from .._models.human_message import HumanMessage
from .._models.system_message import SystemMessage
from .._models.tool_message import ToolMessage

Message: TypeAlias = (
    SystemMessage | HumanMessage | AIMessage | AIMessageChunk | ToolMessage
)
