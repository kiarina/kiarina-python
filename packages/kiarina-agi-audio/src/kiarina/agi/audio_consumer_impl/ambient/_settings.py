from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.audio_embedding_model import (
    AudioEmbeddingModelSpecifier,
)
from kiarina.agi.audio_tagging_model import (
    AudioTaggingModelSpecifier,
)


class AmbientAudioConsumerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SENSOR_AUDIO_CONSUMER_IMPL_AMBIENT_",
        extra="ignore",
    )

    window_samples: int | None = None
    window_seconds: float | None = None
    top_k: int = 3
    tag_threshold: float | None = None
    audio_tagging_model: AudioTaggingModelSpecifier | None = None
    audio_embedding_model: AudioEmbeddingModelSpecifier = "sound"


settings_manager = SettingsManager(AmbientAudioConsumerSettings)
