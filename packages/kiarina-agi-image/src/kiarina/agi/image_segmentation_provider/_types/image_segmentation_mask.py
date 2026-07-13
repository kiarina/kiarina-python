from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

ImageSegmentationMask: TypeAlias = NDArray[np.uint8]
"""Binary mask shaped as [height, width], values 0 or 255."""
