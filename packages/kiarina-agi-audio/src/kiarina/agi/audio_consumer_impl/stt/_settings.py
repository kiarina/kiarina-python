from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.asr_model import ASRModelSpecifier
from kiarina.agi.audio_embedding_model import (
    AudioEmbeddingModelSpecifier,
)
from kiarina.agi.scd_model import SCDModelSpecifier
from kiarina.agi.vad_model import VADModelSpecifier


class STTAudioConsumerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SENSOR_AUDIO_CONSUMER_IMPL_STT_",
        extra="ignore",
    )

    vad_model: VADModelSpecifier | None = None
    scd_model: SCDModelSpecifier | None = None
    asr_model: ASRModelSpecifier | None = None
    diarization_enabled: bool = False
    audio_embedding_model: AudioEmbeddingModelSpecifier = "speaker"

    vad_threshold: float | None = None
    min_silence_ms: int | None = None
    voice_pad_ms: int | None = None

    scd_threshold: float | None = None
    overlap_margin: float | None = None
    min_change_ms: int | None = None
    min_speech_ms: int | None = None

    speaker_similarity_threshold: float = 0.45


settings_manager = SettingsManager(STTAudioConsumerSettings)
