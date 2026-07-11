from dataclasses import dataclass


@dataclass
class VideoMetadata:
    width: int
    height: int
    fps: float
