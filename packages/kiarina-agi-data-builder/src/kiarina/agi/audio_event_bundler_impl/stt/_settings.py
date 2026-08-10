from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class STTAudioEventBundlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_DATA_BUILDER_AUDIO_EVENT_BUNDLER_IMPL_STT_",
        extra="ignore",
    )


settings_manager = SettingsManager(STTAudioEventBundlerSettings)
