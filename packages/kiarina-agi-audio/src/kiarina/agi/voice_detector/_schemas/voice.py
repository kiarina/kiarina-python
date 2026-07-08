from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.audio_types import MonoSamples


@dataclass
class Voice:
    samples: MonoSamples
    """Mono voice samples shaped as [Samples] (always 1D)."""

    sample_rate: int

    start_timestamp: float
    """Best-effort Unix timestamp of the first sample in seconds."""

    end_timestamp: float
    """Best-effort Unix timestamp of the last voice sample in seconds."""

    metadata: dict[str, Any] = field(default_factory=dict)
