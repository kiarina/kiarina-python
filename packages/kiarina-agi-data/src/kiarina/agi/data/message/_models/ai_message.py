from typing import Literal, Self

from pydantic import Field

from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.data.content import Content
from kiarina.agi.data.file_info import FileInfo

from .base_message import BaseMessage
from .tool_call import ToolCall


class AIMessage(BaseMessage):
    type: Literal["ai"] = Field(default="ai", frozen=True)
    tool_calls: list[ToolCall] = Field(default_factory=list)

    def to_estimates(self) -> ChatEstimates:
        estimates = super().to_estimates()

        if self.tool_calls:
            estimates = sum(
                [tool_call.to_estimates() for tool_call in self.tool_calls],
                estimates,
            )

        return estimates

    def to_text(self) -> str:
        contents_text = super().to_text()

        if not self.tool_calls:
            return contents_text

        tool_calls_text = (
            f"<tool_calls>\n"
            f"{'\n'.join([tc.to_text() for tc in self.tool_calls])}\n"
            f"</tool_calls>"
        )

        return f"{contents_text}\n\n{tool_calls_text}".strip()

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        *,
        tool_calls: list[ToolCall] | None = None,
    ) -> Self:
        return cls(
            contents=[
                Content(
                    text=text,
                    files=files if files is not None else [],
                )
            ],
            tool_calls=tool_calls if tool_calls is not None else [],
        )
