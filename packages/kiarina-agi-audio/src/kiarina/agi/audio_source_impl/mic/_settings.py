from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MicAudioSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_SOURCE_IMPL_MIC_",
        extra="ignore",
    )

    device: int | str | None = None
    max_queue_size: int = 100
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 512


settings_manager = SettingsManager(MicAudioSourceSettings)
