from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FileAudioSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_SOURCE_IMPL_FILE_",
        extra="ignore",
    )

    chunk_size: int = 512

    sample_rate: int | None = None
    """Output sample rate; defaults to the audio file sample rate."""

    channels: int | None = None
    """Output channel count; defaults to the audio file channel count."""

    start_timestamp: float | None = None
    """Unix timestamp of the first sample; defaults to open() time."""


settings_manager = SettingsManager(FileAudioSourceSettings)
