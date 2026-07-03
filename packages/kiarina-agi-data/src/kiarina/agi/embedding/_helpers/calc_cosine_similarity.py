from typing import TypeAlias

import numpy as np

from .._schemas.embedding import Embedding
from .._types.embedding_vector import EmbeddingVector

EmbeddingLike: TypeAlias = Embedding | np.ndarray


def calc_cosine_similarity(x: EmbeddingLike, y: EmbeddingLike) -> float:
    if isinstance(x, Embedding) and isinstance(y, Embedding):
        if x.space_id != y.space_id:
            raise ValueError(
                "Cannot compare embeddings from different spaces: "
                f"{x.space_id!r} != {y.space_id!r}"
            )

    return _calc_cosine_similarity(_to_numpy(x), _to_numpy(y))


def _to_numpy(value: EmbeddingLike) -> EmbeddingVector:
    if isinstance(value, Embedding):
        return value.to_numpy()

    return np.asarray(value, dtype=np.float32)


def _calc_cosine_similarity(x: EmbeddingVector, y: EmbeddingVector) -> float:
    if x.ndim != 1:
        raise ValueError(f"Expected x to be a 1D vector, got shape {x.shape}")

    if y.ndim != 1:
        raise ValueError(f"Expected y to be a 1D vector, got shape {y.shape}")

    if x.shape != y.shape:
        return float("-inf")

    x_norm = float(np.linalg.norm(x))
    y_norm = float(np.linalg.norm(y))

    if x_norm == 0.0 or y_norm == 0.0:
        return 0.0

    return float(np.dot(x, y) / (x_norm * y_norm))
