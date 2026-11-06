from pydantic import BaseModel, Field

from kiarina.agi.run_context import RunContext


class ChatProxyMissingFilesRequest(BaseModel):
    """Asks the chat proxy which of these file hashes it does not have."""

    sha256s: list[str] = Field(
        title="SHA-256s", description="The hex SHA-256 of each file to check."
    )
    run_context: RunContext = Field(
        title="Run Context", description="The caller's run context."
    )
