from typing import Any, Literal, Self

from pydantic import Field

from kiarina.agi.data.content import Content
from kiarina.agi.data.display_content import DisplayContent
from kiarina.agi.data.file_info import FileInfo

from .base_message import BaseMessage


class ToolMessage(BaseMessage):
    type: Literal["tool"] = Field(default="tool", frozen=True)
    tool_name: str
    tool_call_args: dict[str, Any] = Field(default_factory=dict)
    tool_call_id: str
    return_direct: bool = False
    failed: bool = False
    artifact: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    display_contents: list[DisplayContent] = Field(default_factory=list)

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
            contents=[
                Content(
                    text=text,
                    files=files if files is not None else [],
                )
            ],
            tool_name=tool_name,
            tool_call_args=tool_call_args if tool_call_args is not None else {},
            tool_call_id=tool_call_id,
        )

    def __str__(self) -> str:
        if action := self.tool_call_args.get("action"):
            return f"{self.tool_name}:{action}"
        else:
            return f"{self.tool_name}"
