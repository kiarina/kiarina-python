from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.audio_embedding_provider import (
    AudioEmbeddingProviderName,
)


class AudioEmbeddingModelConfig(BaseModel):
    provider_name: AudioEmbeddingProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
