from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.audio_consumer import AudioConsumerSpecifier
from kiarina.agi.audio_event_bundler import AudioEventBundlerSpecifier
from kiarina.agi.audio_source import AudioSourceSpecifier


class AudioFileInfoBuilderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FILE_INFO_BUILDER_IMPL_AUDIO_",
        extra="ignore",
    )

    analysis_enabled: bool = False

    audio_source: AudioSourceSpecifier = "file?sample_rate=16000&start_timestamp=0.0"

    audio_consumers: list[AudioConsumerSpecifier] = Field(
        default_factory=lambda: [
            "stt?diarization_enabled=true",
            "ambient?window_seconds=10.0&top_k=3",
        ]
    )

    audio_event_bundlers: list[AudioEventBundlerSpecifier] = Field(
        default_factory=lambda: ["stt", "ambient"]
    )


settings_manager = SettingsManager(AudioFileInfoBuilderSettings)
