from dataclasses import dataclass


@dataclass
class VideoMetadata:
    duration: float
    width: int
    height: int
    fps: float
    total_frames: int
    has_audio_track: bool
