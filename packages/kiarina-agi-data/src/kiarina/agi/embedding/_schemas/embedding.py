from datetime import datetime, timezone
from typing import Any, Self

import numpy as np
import ulid
from pydantic import BaseModel, Field

from .._types.embedding_id import EmbeddingID
from .._types.embedding_kind import EmbeddingKind
from .._types.embedding_space_id import EmbeddingSpaceID
from .._types.embedding_vector import EmbeddingVector


class Embedding(BaseModel):
    id: EmbeddingID = Field(default_factory=lambda: ulid.new().str)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    kind: EmbeddingKind
    space_id: EmbeddingSpaceID
    vector: list[float]
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_numpy(self) -> EmbeddingVector:
        return np.array(self.vector, dtype=np.float32)

    @classmethod
    def from_numpy(
        cls,
        *,
        kind: EmbeddingKind,
        space_id: EmbeddingSpaceID,
        vector: EmbeddingVector,
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        vector = np.asarray(vector, dtype=np.float32)

        if vector.ndim != 1:
            raise ValueError(f"Expected a 1D vector, got shape {vector.shape}")

        return cls(
            kind=kind,
            space_id=space_id,
            vector=vector.astype(float).tolist(),
            metadata=metadata or {},
        )
