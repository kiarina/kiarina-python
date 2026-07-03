from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.text_embedding_provider import TextEmbeddingProviderName


class TextEmbeddingModelConfig(BaseModel):
    provider_name: TextEmbeddingProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
