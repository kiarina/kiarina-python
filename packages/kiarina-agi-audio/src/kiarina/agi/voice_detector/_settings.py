from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class VoiceDetectorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VOICE_DETECTOR_",
        extra="ignore",
    )

    threshold: float = 0.5
    """Speech probability threshold for detecting voice. Range: [0.0, 1.0]"""
    min_silence_ms: int = 500
    """Milliseconds of silence required to end a voice segment."""
    voice_pad_ms: int = 300
    """Padding milliseconds around voice segments."""


settings_manager = SettingsManager(VoiceDetectorSettings)
