from dataclasses import dataclass

from .._types.speaker_probabilities import SpeakerProbabilities


@dataclass
class SCDResult:
    speaker_probabilities: SpeakerProbabilities
    frame_ms: float
