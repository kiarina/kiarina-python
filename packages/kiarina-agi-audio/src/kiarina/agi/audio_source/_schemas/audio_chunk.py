from dataclasses import dataclass

from kiarina.agi.audio_types import MultiChannelSamples


@dataclass
class AudioChunk:
    samples: MultiChannelSamples
    """Audio samples shaped as [Channels, Samples] (always 2D, dtype=float32)."""

    sample_rate: int

    timestamp: float
    """Best-effort Unix timestamp of the first sample in seconds."""
