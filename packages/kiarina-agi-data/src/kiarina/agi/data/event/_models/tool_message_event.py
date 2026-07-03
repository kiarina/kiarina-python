from typing import Any, Literal, Self

from pydantic import Field

from kiarina.agi.data.file_info import FileInfo
from kiarina.agi.data.message import ToolMessage

from .base_event import BaseEvent


class ToolMessageEvent(BaseEvent):
    type: Literal["tool_message"] = Field(default="tool_message", frozen=True)
    message: ToolMessage

    def to_text(self) -> str:
        return self.message.to_text()

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        *,
        tool_name: str,
        tool_call_args: dict[str, Any] | None = None,
        tool_call_id: str,
    ) -> Self:
        return cls(
            message=ToolMessage.create(
                text,
                files,
                tool_name=tool_name,
                tool_call_args=tool_call_args,
                tool_call_id=tool_call_id,
            )
        )
