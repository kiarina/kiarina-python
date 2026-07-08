from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockTTSProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TTS_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    result_audio_file_path: str | None = None


settings_manager = SettingsManager(MockTTSProviderSettings)
