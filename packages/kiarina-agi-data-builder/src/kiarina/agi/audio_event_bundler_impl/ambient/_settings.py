from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class AmbientAudioEventBundlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_DATA_BUILDER_AUDIO_EVENT_BUNDLER_IMPL_AMBIENT_",
        extra="ignore",
    )

    change_similarity_threshold: float = 0.55


settings_manager = SettingsManager(AmbientAudioEventBundlerSettings)
