from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class RapidOCRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_OCR_PROVIDER_IMPL_RAPIDOCR_",
        extra="ignore",
    )

    text_score: float = Field(default=0.5, ge=0.0, le=1.0)
    box_threshold: float = Field(default=0.5, ge=0.0, le=1.0)


settings_manager = SettingsManager(RapidOCRProviderSettings)
