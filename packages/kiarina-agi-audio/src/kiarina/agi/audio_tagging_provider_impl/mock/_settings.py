from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockAudioTaggingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_TAGGING_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    predictions: list[tuple[str, float]] = Field(
        default_factory=lambda: [
            ("Speech", 0.9),
            ("Music", 0.05),
            ("Silence", 0.05),
        ]
    )


settings_manager = SettingsManager(MockAudioTaggingProviderSettings)
