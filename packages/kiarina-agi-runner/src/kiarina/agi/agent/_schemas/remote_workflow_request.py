from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.history import History


class RemoteWorkflowRequest(BaseModel):
    """Transport-neutral request for delegating one Agent workflow run."""

    request_id: str
    history: History
    metadata: dict[str, Any] = Field(default_factory=dict)
