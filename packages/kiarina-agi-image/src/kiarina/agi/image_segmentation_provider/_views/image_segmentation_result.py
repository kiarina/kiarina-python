from dataclasses import dataclass

from .._types.image_segmentation_confidence_map import (
    ImageSegmentationConfidenceMap,
)
from .._types.image_segmentation_mask import ImageSegmentationMask


@dataclass
class ImageSegmentationResult:
    """A binary segmentation mask and optional per-pixel confidence map."""

    mask: ImageSegmentationMask
    confidence_map: ImageSegmentationConfidenceMap | None = None
