from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.ocr_model_config import OCRModelConfig
from ._types.ocr_model_alias import OCRModelAlias
from ._types.ocr_model_name import OCRModelName
from ._types.ocr_model_specifier import OCRModelSpecifier


class OCRModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_OCR_MODEL_",
        extra="ignore",
    )

    default: OCRModelSpecifier = "rapidocr"

    aliases: dict[OCRModelAlias, OCRModelName] = Field(
        default_factory=lambda: {"ocr": "rapidocr"}
    )
    presets: dict[OCRModelName, OCRModelConfig] = Field(
        default_factory=lambda: {
            "mock": OCRModelConfig(provider_name="mock"),
            "rapidocr": OCRModelConfig(provider_name="rapidocr"),
        }
    )
    customs: dict[OCRModelName, OCRModelConfig] = Field(default_factory=dict)


settings_manager = SettingsManager(OCRModelSettings)
