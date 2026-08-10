from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.ocr_provider import OCRResult


class MockOCRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_OCR_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    results: list[OCRResult] = Field(
        default_factory=lambda: [
            OCRResult(
                text="Hello, world!",
                score=0.9,
                polygon=[[0.1, 0.1], [0.9, 0.1], [0.9, 0.2], [0.1, 0.2]],
            )
        ]
    )


settings_manager = SettingsManager(MockOCRProviderSettings)
