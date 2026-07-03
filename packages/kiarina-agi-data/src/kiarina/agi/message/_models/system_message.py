from typing import Literal, Self

from pydantic import Field

from kiarina.agi.content import Content
from kiarina.agi.file_info import FileInfo

from .base_message import BaseMessage


class SystemMessage(BaseMessage):
    type: Literal["system"] = Field(default="system", frozen=True)

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
