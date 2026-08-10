from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.ocr_provider import OCRProviderName


class OCRModelConfig(BaseModel):
    provider_name: OCRProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
