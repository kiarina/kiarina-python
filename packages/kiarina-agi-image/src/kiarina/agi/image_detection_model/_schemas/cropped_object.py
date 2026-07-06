from dataclasses import dataclass, field

from kiarina.agi.image_detection_provider import KeypointType
from kiarina.agi.image_types import ImagePixels


@dataclass
class CroppedObject:
    pixels: ImagePixels

    score: float
    """Detection confidence (0.0 ~ 1.0)."""

    label: str
    """Human-readable label, e.g. "face", "chair", "dog"."""

    keypoint_type: KeypointType | None = None
    """Layout of ``keypoints``. None when there are no keypoints."""

    keypoints: list[list[float]] = field(default_factory=list)
    """Keypoint coordinates [[x, y], ...], normalized to the crop / bbox
    (0.0 ~ 1.0 inside the bbox), ordered per ``keypoint_type``. Points lying
    outside the bbox fall outside [0, 1] and are not clipped."""
