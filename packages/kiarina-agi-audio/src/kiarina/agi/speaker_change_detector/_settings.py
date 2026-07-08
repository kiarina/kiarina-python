from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SpeakerChangeDetectorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SPEAKER_CHANGE_DETECTOR_",
        extra="ignore",
    )

    threshold: float = 0.5
    """Speaker probability threshold for detecting an active speaker."""

    overlap_margin: float = 0.1
    """Top-two probability margin under which multi-speaker frames are overlap."""

    min_change_ms: int = 100
    """Minimum duration for a speaker state change to survive smoothing."""

    min_speech_ms: int = 100
    """Minimum duration for an emitted speech segment."""


settings_manager = SettingsManager(SpeakerChangeDetectorSettings)
