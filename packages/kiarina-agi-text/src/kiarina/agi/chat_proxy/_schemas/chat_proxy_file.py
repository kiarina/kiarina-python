from pydantic import BaseModel, Field


class ChatProxyFile(BaseModel):
    """
    A media file the chat proxy cannot read from its own storage. The caller sends
    the contents only when the proxy may not have them yet; the proxy answers 409
    with the hashes it lacks.
    """

    mime_type: str = Field(title="MIME Type", description="The file's MIME type.")
    sha256: str = Field(title="SHA-256", description="The hex SHA-256 of the bytes.")
    base64_data: str | None = Field(
        default=None,
        title="Base64 Data",
        description="The file's bytes, base64-encoded, or None to use the proxy's copy.",
    )
