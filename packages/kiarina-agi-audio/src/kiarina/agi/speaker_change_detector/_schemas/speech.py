from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.audio_types import MonoSamples

from .._types.speaker_kind import SpeakerKind


@dataclass
class Speech:
    samples: MonoSamples
    sample_rate: int
    start_timestamp: float
    end_timestamp: float
    speaker_index: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def kind(self) -> SpeakerKind:
        if self.speaker_index == -1:
            return "unknown_silence"

        if self.speaker_index == -2:
            return "unknown_overlap"

        return "speaker"
