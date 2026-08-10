from kiarina.agi.event import (
    AIMessageEvent,
    CustomEvent,
    Event,
    HumanMessageEvent,
    ToolMessageEvent,
)
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from kiarina.agi.message_builder import build_message
from kiarina.agi.run_context import RunContext

from .._types.event_input import EventInput


async def build_event(
    event_input: EventInput,
    *,
    run_context: RunContext,
) -> Event:
    if isinstance(event_input, Event):
        return event_input

    if isinstance(event_input, tuple) and event_input[0] == "custom":
        return CustomEvent(payload=event_input[1])

    message = await build_message(event_input, run_context=run_context)

    if isinstance(message, HumanMessage):
        return HumanMessageEvent(message=message)
    elif isinstance(message, AIMessage):
        return AIMessageEvent(message=message)
    elif isinstance(message, ToolMessage):
        return ToolMessageEvent(message=message)
    else:  # pragma: no cover
        raise AssertionError(f"Unsupported message type: {type(message)}")
