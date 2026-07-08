from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.scd_provider import SCDProviderName


class SCDModelConfig(BaseModel):
    provider_name: SCDProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
