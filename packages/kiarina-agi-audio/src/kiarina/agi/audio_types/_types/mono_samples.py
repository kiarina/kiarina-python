from typing import TypeAlias

import numpy as np
from jaxtyping import Float32

MonoSamples: TypeAlias = Float32[np.ndarray, "samples"]  # noqa: F821
"""Mono float32 audio samples shaped as [samples]."""
