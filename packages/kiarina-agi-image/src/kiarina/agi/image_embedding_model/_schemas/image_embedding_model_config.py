from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.image_embedding_provider import (
    ImageEmbeddingProviderName,
)


class ImageEmbeddingModelConfig(BaseModel):
    provider_name: ImageEmbeddingProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
