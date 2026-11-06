from pydantic import BaseModel, Field


class ChatProxyMissingFiles(BaseModel):
    """The file hashes the chat proxy does not have, so their contents must be sent."""

    missing: list[str] = Field(
        title="Missing", description="The hex SHA-256 of each file it lacks."
    )
