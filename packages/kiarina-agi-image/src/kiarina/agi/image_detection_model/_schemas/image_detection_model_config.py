from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.image_detection_provider import (
    ImageDetectionProviderName,
)


class ImageDetectionModelConfig(BaseModel):
    provider_name: ImageDetectionProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
