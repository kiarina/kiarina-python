from dataclasses import dataclass

from kiarina.agi.audio_types import AudioSamples


@dataclass
class AudioWindow:
    samples: AudioSamples
    """Audio samples for this window."""

    sample_rate: int

    start_timestamp: float
    """Best-effort timestamp of the first sample in seconds."""

    end_timestamp: float
    """Best-effort timestamp immediately after the final sample in seconds."""
