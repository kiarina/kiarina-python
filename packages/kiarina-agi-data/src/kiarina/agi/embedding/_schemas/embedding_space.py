from typing import Any

from pydantic import BaseModel, Field

from .._types.embedding_kind import EmbeddingKind
from .._types.embedding_space_id import EmbeddingSpaceID


class EmbeddingSpace(BaseModel):
    kind: EmbeddingKind
    space_id: EmbeddingSpaceID
    dimension: int
    metadata: dict[str, Any] = Field(default_factory=dict)
