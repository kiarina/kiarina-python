from typing import Literal

from pydantic import BaseModel, Field, model_validator

from kiarina.agi.event import Event


class RemoteWorkflowResult(BaseModel):
    """Transport-neutral result returned by a delegated Agent workflow run."""

    request_id: str
    status: Literal["completed", "failed"]
    events: list[Event] = Field(default_factory=list)
    error: str | None = None

    @model_validator(mode="after")
    def validate_status_payload(self) -> "RemoteWorkflowResult":
        if self.status == "completed" and self.error is not None:
            raise ValueError("Completed result cannot include an error")
        if self.status == "failed" and not self.error:
            raise ValueError("Failed result requires an error")
        return self
