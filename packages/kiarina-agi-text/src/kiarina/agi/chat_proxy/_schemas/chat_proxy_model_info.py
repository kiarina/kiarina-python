from pydantic import BaseModel, Field

from kiarina.agi.chat_provider import ChatCapabilities


class ChatProxyModelInfo(BaseModel):
    """A chat model on the chat proxy."""

    name: str = Field(title="Name", description="The resolved chat model name.")
    capabilities: ChatCapabilities = Field(
        title="Capabilities", description="The chat model's capabilities."
    )
