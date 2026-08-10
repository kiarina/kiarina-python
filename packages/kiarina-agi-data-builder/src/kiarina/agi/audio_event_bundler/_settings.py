from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.audio_event_bundler_name import AudioEventBundlerName


class AudioEventBundlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_EVENT_BUNDLER_",
        extra="ignore",
    )

    presets: dict[AudioEventBundlerName, ImportPath] = Field(
        default_factory=lambda: {
            "ambient": "kiarina.agi.audio_event_bundler_impl.ambient:create_ambient_audio_event_bundler",
            "stt": "kiarina.agi.audio_event_bundler_impl.stt:create_stt_audio_event_bundler",
        }
    )

    customs: dict[AudioEventBundlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(AudioEventBundlerSettings)
