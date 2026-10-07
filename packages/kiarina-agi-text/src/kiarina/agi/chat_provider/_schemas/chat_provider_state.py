from typing import Any, Self

from pydantic import BaseModel, Field

from kiarina.agi.message import Message

from .._constants.chat_provider_state_key import CHAT_PROVIDER_STATE_KEY
from .._types.chat_provider_name import ChatProviderName


class ChatProviderState(BaseModel):
    """
    What a chat provider keeps on the `AIMessage` it returns, to continue from it
    in a later request, such as a thread to resume or reasoning to send back.

    It is kept in `metadata["chat_provider"]`. A provider uses it only when the
    name is its own and `history_hash` still matches what the state depends on,
    so edits make it start fresh. It is only an optimization.
    """

    name: ChatProviderName

    history_hash: str
    """
    The hash of what the state depends on: `compute_history_hash` of the history
    up to this message as the provider sends it, for a thread, or
    `compute_message_hash` of this message, for its reasoning.
    """

    data: dict[str, Any] = Field(default_factory=dict)
    """Provider-specific state."""

    @classmethod
    def from_message(cls, message: Message, name: ChatProviderName) -> Self | None:
        """The state on `message` if the provider named `name` wrote it."""
        value = message.metadata.get(CHAT_PROVIDER_STATE_KEY)

        if not isinstance(value, dict) or value.get("name") != name:
            return None

        try:
            return cls.model_validate(value)
        except ValueError:
            return None

    def write_to(self, message: Message) -> None:
        """Keep the state on `message`, replacing any other provider's."""
        message.metadata[CHAT_PROVIDER_STATE_KEY] = self.model_dump(mode="json")
