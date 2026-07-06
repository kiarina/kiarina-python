from dataclasses import dataclass, field

from .._types.keypoint_type import KeypointType


@dataclass
class DetectedObject:
    bbox: list[float]
    """[x1, y1, x2, y2], normalized to the source image (0.0 ~ 1.0)."""

    score: float
    """Detection confidence (0.0 ~ 1.0)."""

    label: str
    """Human-readable label, e.g. "face", "chair", "dog"."""

    keypoint_type: KeypointType | None = None
    """Layout of ``keypoints``. None when the provider returns no keypoints."""

    keypoints: list[list[float]] = field(default_factory=list)
    """Keypoint coordinates [[x, y], ...], normalized (0.0 ~ 1.0), ordered per
    ``keypoint_type``."""
