from typing import TypeAlias

import numpy as np
from jaxtyping import Float32

EmbeddingVector: TypeAlias = Float32[np.ndarray, "dimensions"]  # noqa: F821
"""Float32 embedding vector shaped as [dimensions]."""
