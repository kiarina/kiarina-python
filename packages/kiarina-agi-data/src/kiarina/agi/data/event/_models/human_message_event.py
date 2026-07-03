from typing import Literal, Self

from pydantic import Field

from kiarina.agi.data.file_info import FileInfo
from kiarina.agi.data.message import HumanMessage

from .base_event import BaseEvent


class HumanMessageEvent(BaseEvent):
    type: Literal["human_message"] = Field(default="human_message", frozen=True)
    message: HumanMessage

    def to_text(self) -> str:
        return self.message.to_text()

    @classmethod
    def create(cls, text: str = "", files: list[FileInfo] | None = None) -> Self:
        return cls(message=HumanMessage.create(text, files))
