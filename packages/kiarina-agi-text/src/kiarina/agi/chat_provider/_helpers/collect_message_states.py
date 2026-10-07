from typing import Any

from kiarina.agi.message import Message

from .._operations.compute_message_hashes import compute_message_hashes
from .._schemas.chat_provider_state import ChatProviderState
from .._types.chat_provider_name import ChatProviderName


def collect_message_states(
    messages: list[Message], name: ChatProviderName, **context: Any
) -> dict[int, ChatProviderState]:
    """
    The states the provider named `name` wrote on AI messages, by message index,
    where `history_hash` still matches `compute_message_hashes(messages, **context)`
    at that message. A change to that message or anything before it, or another
    model in `context`, leaves the state out.
    """
    states: dict[int, ChatProviderState] = {}
    hashes: list[str] | None = None

    for index, message in enumerate(messages):
        if message.type not in ("ai", "ai_chunk"):
            continue

        state = ChatProviderState.from_message(message, name)

        if state is None:
            continue

        if hashes is None:
            hashes = compute_message_hashes(messages, **context)

        if state.history_hash == hashes[index]:
            states[index] = state

    return states
