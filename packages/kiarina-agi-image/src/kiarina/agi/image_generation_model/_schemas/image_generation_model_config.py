from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.image_generation_provider import ImageGenerationProviderName


class ImageGenerationModelConfig(BaseModel):
    provider_name: ImageGenerationProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
