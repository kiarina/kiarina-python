from pydantic import BaseModel

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.chat_limits import ChatLimits


class ChatOverflow(BaseModel):
    limits: ChatLimits

    estimates: ChatEstimates

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def token_count(self) -> int:
        return max(0, self.estimates.token_count - self.limits.token_count_limit)

    @property
    def file_size(self) -> int:
        return max(0, self.estimates.file_size - self.limits.file_size_limit)

    @property
    def image_file_count(self) -> int:
        return max(
            0, self.estimates.image_file_count - self.limits.image_file_count_limit
        )

    @property
    def audio_duration(self) -> float:
        return max(
            0.0, self.estimates.audio_duration - self.limits.audio_duration_limit
        )

    @property
    def audio_file_count(self) -> int:
        return max(
            0, self.estimates.audio_file_count - self.limits.audio_file_count_limit
        )

    @property
    def video_duration(self) -> float:
        return max(
            0.0, self.estimates.video_duration - self.limits.video_duration_limit
        )

    @property
    def video_file_count(self) -> int:
        return max(
            0, self.estimates.video_file_count - self.limits.video_file_count_limit
        )

    @property
    def pdf_page_count(self) -> int:
        return max(0, self.estimates.pdf_page_count - self.limits.pdf_page_count_limit)

    @property
    def pdf_file_count(self) -> int:
        return max(0, self.estimates.pdf_file_count - self.limits.pdf_file_count_limit)

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def is_overflow(self) -> bool:
        return (
            self.token_count > 0
            or self.file_size > 0
            or self.image_file_count > 0
            or self.audio_duration > 0
            or self.audio_file_count > 0
            or self.video_duration > 0
            or self.video_file_count > 0
            or self.pdf_page_count > 0
            or self.pdf_file_count > 0
        )
