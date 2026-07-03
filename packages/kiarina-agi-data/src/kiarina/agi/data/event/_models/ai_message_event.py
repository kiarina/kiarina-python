from typing import Literal, Self

from pydantic import Field

from kiarina.agi.data.file_info import FileInfo
from kiarina.agi.data.message import AIMessage, ToolCall

from .base_event import BaseEvent


class AIMessageEvent(BaseEvent):
    type: Literal["ai_message"] = Field(default="ai_message", frozen=True)
    message: AIMessage

    def to_text(self) -> str:
        return self.message.to_text()

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        tool_calls: list[ToolCall] | None = None,
    ) -> Self:
        return cls(message=AIMessage.create(text, files, tool_calls=tool_calls))
