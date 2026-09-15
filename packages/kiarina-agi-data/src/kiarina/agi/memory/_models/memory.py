from datetime import datetime, timezone
from typing import Any

import ulid
from pydantic import BaseModel, Field

from kiarina.agi.file import URIOrFilePath

from .._types.memory_id import MemoryID
from .._types.memory_type import MemoryType


class Memory(BaseModel):
    id: MemoryID = Field(default_factory=lambda: MemoryID(str(ulid.new())), frozen=True)
    type: MemoryType = Field(frozen=True)
    version: int = 1
    """Type and version determine the structures of text, asset_uri, vector, and metadata."""
    text: str = ""
    asset_uri: URIOrFilePath | None = None
    vector: list[float] | None = None
    edit_protected: bool = False
    delete_protected: bool = False
    activated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """The time when the memory was explicitly used in cognition, rather than merely read."""
    metadata: dict[str, Any] = Field(default_factory=dict)
