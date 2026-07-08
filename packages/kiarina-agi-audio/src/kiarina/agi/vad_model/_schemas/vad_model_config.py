from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.vad_provider import VADProviderName


class VADModelConfig(BaseModel):
    provider_name: VADProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
