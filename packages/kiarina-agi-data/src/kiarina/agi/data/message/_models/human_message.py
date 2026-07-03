from typing import Literal, Self

from pydantic import Field

from kiarina.agi.data.content import Content
from kiarina.agi.data.file_info import FileInfo

from .base_message import BaseMessage


class HumanMessage(BaseMessage):
    type: Literal["human"] = Field(default="human", frozen=True)

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
    ) -> Self:
        return cls(
            contents=[
                Content(
                    text=text,
                    files=files if files is not None else [],
                )
            ]
        )
