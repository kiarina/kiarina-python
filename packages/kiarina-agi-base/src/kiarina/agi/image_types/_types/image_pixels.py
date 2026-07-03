from typing import TypeAlias

import numpy as np
from jaxtyping import UInt8

ImagePixels: TypeAlias = UInt8[np.ndarray, "height width rgb"]  # noqa: F722
"""RGB image pixels shaped as [height, width, rgb], dtype uint8."""
