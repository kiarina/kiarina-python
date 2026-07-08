from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.asr_provider import ASRProviderName


class ASRModelConfig(BaseModel):
    provider_name: ASRProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
