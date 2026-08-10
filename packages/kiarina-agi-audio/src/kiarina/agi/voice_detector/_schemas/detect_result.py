from dataclasses import dataclass

from kiarina.agi.vad_provider import SpeechProbability

from .voice import Voice


@dataclass
class DetectResult:
    is_voice: bool
    probability: SpeechProbability
    voice: Voice | None = None
