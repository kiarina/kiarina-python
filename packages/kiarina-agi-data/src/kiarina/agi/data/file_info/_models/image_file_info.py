from typing import Any, Literal

from pydantic import Field

from kiarina.agi.data.chat_estimates import ChatEstimates

from .base_file_info import BaseFileInfo


class ImageFileInfo(BaseFileInfo):
    type: Literal["image"] = Field(default="image", frozen=True)
    tag: str = "image_file"
    width: int
    height: int

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs = super().xml_attributes
        attrs["width"] = self.width
        attrs["height"] = self.height
        return attrs

    def to_content_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()
        estimates.add_token_count("image", self.token_count)
        estimates.image_file_count = 1
        estimates.file_size = self.file_size
        return estimates
