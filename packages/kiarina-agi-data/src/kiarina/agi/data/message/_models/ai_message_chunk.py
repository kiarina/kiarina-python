from typing import Literal

from pydantic import Field

from .ai_message import AIMessage
from .tool_call_chunk import ToolCallChunk


class AIMessageChunk(AIMessage):
    type: Literal["ai_chunk"] = Field(default="ai_chunk", frozen=True)  # type: ignore[assignment]
    tool_call_chunks: list[ToolCallChunk] = Field(default_factory=list)
