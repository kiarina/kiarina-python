from dataclasses import dataclass

from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.embedding import Embedding
from kiarina.agi.speaker_change_detector import Speech


@dataclass(kw_only=True)
class STTAudioEvent(AudioEvent):
    speech: Speech
    text: str
    embedding: Embedding | None
