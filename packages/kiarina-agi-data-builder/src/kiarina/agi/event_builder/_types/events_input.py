from collections.abc import Sequence

from .event_input import EventInput

EventsInput = EventInput | Sequence[EventInput]
