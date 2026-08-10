from typing import Any, Literal

from pydantic import Field

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.file_utils import normalize_time

from .base_file_info import BaseFileInfo


class AudioFileInfo(BaseFileInfo):
    type: Literal["audio"] = Field(default="audio", frozen=True)
    tag: str = "audio_file"
    start_time: float = 0.0
    end_time: float = -1.0
    duration: float

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs = super().xml_attributes

        if not self.start_time == 0.0 or not self.end_time == -1.0:
            attrs["start_time"] = self.normalized_start_time
            attrs["end_time"] = self.normalized_end_time

        attrs["duration"] = self.segment_duration

        return attrs

    @property
    def optional_export_fields(self) -> tuple[str, ...]:
        return (*super().optional_export_fields, "start_time", "end_time")

    @property
    def normalized_start_time(self) -> float:
        return normalize_time(self.start_time, self.duration)

    @property
    def normalized_end_time(self) -> float:
        return normalize_time(self.end_time, self.duration)

    @property
    def segment_duration(self) -> float:
        return self.normalized_end_time - self.normalized_start_time

    def to_content_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()
        estimates.add_token_count("audio", self.token_count)
        estimates.audio_file_count = 1
        estimates.audio_duration = self.segment_duration
        estimates.file_size = self.file_size
        return estimates
