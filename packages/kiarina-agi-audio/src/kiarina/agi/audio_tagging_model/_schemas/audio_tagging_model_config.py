from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.audio_tagging_provider import (
    AudioTaggingProviderName,
)


class AudioTaggingModelConfig(BaseModel):
    provider_name: AudioTaggingProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
