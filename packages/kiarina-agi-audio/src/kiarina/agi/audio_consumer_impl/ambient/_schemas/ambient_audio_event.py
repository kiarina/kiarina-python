from dataclasses import dataclass, field

from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.audio_tagging_provider import AudioTagPrediction
from kiarina.agi.embedding import Embedding


@dataclass(kw_only=True)
class AmbientAudioEvent(AudioEvent):
    start_timestamp: float
    end_timestamp: float
    predictions: list[AudioTagPrediction] = field(default_factory=list)
    embedding: Embedding
