from typing import Any

from kiarina.agi.message import Message

from .._operations.compute_message_hash import compute_message_hash
from .._schemas.chat_provider_state import ChatProviderState
from .._types.chat_provider_name import ChatProviderName


def collect_message_states(
    messages: list[Message], name: ChatProviderName, **context: Any
) -> dict[int, ChatProviderState]:
    """
    The states the provider named `name` wrote on AI messages, by message index,
    where `history_hash` is still `compute_message_hash(message, **context)`.
    An edited message, or one from another model in `context`, is left out.
    """
    states: dict[int, ChatProviderState] = {}

    for index, message in enumerate(messages):
        if message.type not in ("ai", "ai_chunk"):
            continue

        state = ChatProviderState.from_message(message, name)

        if state and state.history_hash == compute_message_hash(message, **context):
            states[index] = state

    return states
