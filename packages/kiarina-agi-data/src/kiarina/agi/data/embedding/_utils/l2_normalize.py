import numpy as np

from .._types.embedding_vector import EmbeddingVector


def l2_normalize(vector: np.ndarray) -> EmbeddingVector:
    vector = np.asarray(vector, dtype=np.float32)
    norm = float(np.linalg.norm(vector))

    if norm == 0.0:
        return vector

    return (vector / norm).astype(np.float32)
