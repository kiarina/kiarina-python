from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.audio_consumer_name import AudioConsumerName


class AudioConsumerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_CONSUMER_",
        extra="ignore",
    )

    presets: dict[AudioConsumerName, ImportPath] = Field(
        default_factory=lambda: {
            "ambient": "kiarina.agi.audio_consumer_impl.ambient:create_ambient_audio_consumer",
            "stt": "kiarina.agi.audio_consumer_impl.stt:create_stt_audio_consumer",
        }
    )

    customs: dict[AudioConsumerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(AudioConsumerSettings)
