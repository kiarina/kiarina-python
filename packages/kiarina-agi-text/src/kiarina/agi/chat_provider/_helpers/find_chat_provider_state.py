from kiarina.agi.message import Message

from .._schemas.chat_provider_state import ChatProviderState
from .._types.chat_provider_name import ChatProviderName


def find_chat_provider_state(
    messages: list[Message], name: ChatProviderName
) -> tuple[int, ChatProviderState] | None:
    """
    The index and state of the last AI message, if the provider named `name`
    wrote its state. A later AI message from anywhere else hides older state.
    """
    for index in range(len(messages) - 1, -1, -1):
        if messages[index].type in ("ai", "ai_chunk"):
            state = ChatProviderState.from_message(messages[index], name)
            return (index, state) if state else None

    return None
