from typing import cast

from kiarina.agi.event import Event
from kiarina.agi.run_context import RunContext

from .._types.event_input import EventInput
from .._types.events_input import EventsInput
from .build_event import build_event


async def build_events(
    events_input: EventsInput,
    *,
    run_context: RunContext,
) -> list[Event]:
    if isinstance(events_input, list):
        return [
            await build_event(event_input, run_context=run_context)
            for event_input in events_input
        ]

    else:
        events_input = cast(EventInput, events_input)
        return [await build_event(events_input, run_context=run_context)]
