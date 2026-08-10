from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class RequestLogEntry(BaseModel):
    kind: str
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
