from typing import Any, Literal

from pydantic import Field

from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.file_utils import normalize_time

from .base_file_info import BaseFileInfo


class VideoFileInfo(BaseFileInfo):
    type: Literal["video"] = Field(default="video", frozen=True)
    tag: str = "video_file"
    start_time: float = 0.0
    end_time: float = -1.0
    width: int
    height: int
    duration: float

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs = super().xml_attributes

        if not self.start_time == 0.0 or not self.end_time == -1.0:
            attrs["start_time"] = self.normalized_start_time
            attrs["end_time"] = self.normalized_end_time

        attrs["width"] = self.width
        attrs["height"] = self.height
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
        estimates.add_token_count("video", self.token_count)
        estimates.video_file_count = 1
        estimates.video_duration = self.segment_duration
        estimates.file_size = self.file_size
        return estimates
