from typing import Literal

from pydantic import Field

from kiarina.agi.data.message import AIMessageChunk

from .base_event import BaseEvent


class AIMessageChunkEvent(BaseEvent):
    type: Literal["ai_message_chunk"] = Field(default="ai_message_chunk", frozen=True)
    transient: bool = True
    message: AIMessageChunk

    def to_text(self) -> str:
        return self.message.to_text()
