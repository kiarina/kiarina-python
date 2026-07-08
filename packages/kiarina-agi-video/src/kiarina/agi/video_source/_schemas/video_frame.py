from dataclasses import dataclass

from kiarina.agi.image_types import ImagePixels


@dataclass
class VideoFrame:
    pixels: ImagePixels

    timestamp: float
    """Best-effort Unix timestamp of the frame in seconds."""

    frame_index: int
