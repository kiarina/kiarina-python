from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.asr_provider import ASRSegment


class MockASRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASR_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    result_text: str = "Mock speech-to-text result"

    result_segments: list[ASRSegment] = Field(
        default_factory=lambda: [
            ASRSegment(
                text="Hello, this is the first segment.",
                start_timestamp=0.0,
                end_timestamp=2.5,
                metadata={"speaker_name": "Speaker 1"},
            ),
            ASRSegment(
                text="And this is the second segment.",
                start_timestamp=2.5,
                end_timestamp=5.0,
                metadata={"speaker_name": "Speaker 2"},
            ),
        ]
    )


settings_manager = SettingsManager(MockASRProviderSettings)
