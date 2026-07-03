from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.chat_provider import ChatProviderName


class ChatModelConfig(BaseModel):
    provider_name: ChatProviderName
    provider_config: dict[str, Any] = Field(default_factory=dict)
    token_scale_factor: float = 1.0
    visible: bool = True
