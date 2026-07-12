from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.ocr_provider_name import OCRProviderName


class OCRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_OCR_PROVIDER_",
        extra="ignore",
    )

    presets: dict[OCRProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.ocr_provider_impl.mock:create_mock_ocr_provider",
            "rapidocr": "kiarina.agi.ocr_provider_impl.rapidocr:create_rapidocr_provider",
        }
    )
    customs: dict[OCRProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(OCRProviderSettings)
