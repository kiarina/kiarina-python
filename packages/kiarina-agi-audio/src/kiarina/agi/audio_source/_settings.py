from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.audio_source_name import AudioSourceName


class AudioSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_SOURCE_",
        extra="ignore",
    )

    default: AudioSourceName = "mic"

    presets: dict[AudioSourceName, ImportPath] = Field(
        default_factory=lambda: {
            "mic": "kiarina.agi.audio_source_impl.mic:create_mic_audio_source",
            "file": "kiarina.agi.audio_source_impl.file:create_file_audio_source",
            "numpy": "kiarina.agi.audio_source_impl.numpy:create_numpy_audio_source",
            "queue": "kiarina.agi.audio_source_impl.queue:create_queue_audio_source",
        }
    )

    customs: dict[AudioSourceName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(AudioSourceSettings)
