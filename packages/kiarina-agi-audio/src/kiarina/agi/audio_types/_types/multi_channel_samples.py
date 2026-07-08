from typing import TypeAlias

import numpy as np
from jaxtyping import Float32

MultiChannelSamples: TypeAlias = Float32[np.ndarray, "channels samples"]  # noqa: F722
"""Multi-channel float32 audio samples shaped as [channels, samples]."""
