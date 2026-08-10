from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockVADProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VAD_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    sample_rate: int = 16000
    """Expected sample rate; predict() raises if a different rate is passed."""
    speech_probabilities: list[float] = Field(default_factory=lambda: [0.0])
    repeat_last: bool = True


settings_manager = SettingsManager(MockVADProviderSettings)
