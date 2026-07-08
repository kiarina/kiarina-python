from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.tts_provider import TTSProviderName


class TTSModelConfig(BaseModel):
    provider_name: TTSProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
