from pydantic import BaseModel, Field


class ChatProxyFile(BaseModel):
    """The contents of a media file the chat proxy cannot read from its own storage."""

    mime_type: str = Field(title="MIME Type", description="The file's MIME type.")
    base64_data: str = Field(
        title="Base64 Data", description="The file's bytes, base64-encoded."
    )
