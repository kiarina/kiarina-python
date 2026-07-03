from pydantic import BaseModel, Field

from .._types.display_content_type import DisplayContentType


class BaseDisplayContent(BaseModel):
    type: DisplayContentType = Field(frozen=True)
    mime_type: str
