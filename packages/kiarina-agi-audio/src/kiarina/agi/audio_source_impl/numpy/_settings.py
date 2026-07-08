from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class NumpyAudioSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_SOURCE_IMPL_NUMPY_",
        extra="ignore",
    )

    sample_rate: int = 16000
    chunk_size: int = 512
    start_timestamp: float | None = None
    """Unix timestamp of the first sample; defaults to open() time."""


settings_manager = SettingsManager(NumpyAudioSourceSettings)
