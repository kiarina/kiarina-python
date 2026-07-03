from typing import Literal

from pydantic import Field

from .base_display_content import BaseDisplayContent


class TextDisplayContent(BaseDisplayContent):
    type: Literal["text"] = Field(default="text", frozen=True)
    mime_type: str = "text/plain"
    text: str
    start_line: int = 1
