from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

ImageSegmentationConfidenceMap: TypeAlias = NDArray[np.float32]
"""Per-pixel foreground confidence shaped as [height, width], values 0.0 ~ 1.0."""
