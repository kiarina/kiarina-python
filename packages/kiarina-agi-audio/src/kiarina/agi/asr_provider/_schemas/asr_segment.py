from typing import Any

from pydantic import BaseModel, Field

from .._utils.format_time import format_time


class ASRSegment(BaseModel):
    text: str
    start_timestamp: float
    end_timestamp: float
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_srt(self) -> str:
        return (
            f"{format_time(self.start_timestamp, format='srt')} --> "
            f"{format_time(self.end_timestamp, format='srt')}\n"
            f"{self.text}"
        )
