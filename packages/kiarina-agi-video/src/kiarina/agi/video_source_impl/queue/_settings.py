from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class QueueVideoSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_SOURCE_IMPL_QUEUE_",
        extra="ignore",
    )


settings_manager = SettingsManager(QueueVideoSourceSettings)
