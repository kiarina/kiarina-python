from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockSCDProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SCD_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    speaker_probabilities: list[list[float]] | None = None

    frame_ms: float = 100.0

    num_speakers: int = 1

    default_probability: float = 1.0

    metadata: dict[str, object] = Field(default_factory=dict)


settings_manager = SettingsManager(MockSCDProviderSettings)
