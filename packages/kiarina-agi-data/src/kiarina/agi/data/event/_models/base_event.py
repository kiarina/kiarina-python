from datetime import datetime, timezone

import ulid
from pydantic import BaseModel, Field

from .._types.event_type import EventType


class BaseEvent(BaseModel):
    type: EventType = Field(frozen=True)
    id: str = Field(default_factory=lambda: ulid.new().str)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transient: bool = False
    hidden: bool = False

    def to_text(self) -> str:
        return self.id
