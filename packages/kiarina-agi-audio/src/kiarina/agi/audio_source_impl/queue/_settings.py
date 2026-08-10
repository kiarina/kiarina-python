from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class QueueAudioSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_SOURCE_IMPL_QUEUE_",
        extra="ignore",
    )


settings_manager = SettingsManager(QueueAudioSourceSettings)
