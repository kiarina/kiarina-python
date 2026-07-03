from kiarina.agi.data.file_info_pool import FileInfoPool

from .._types.event import Event
from .dehydrate_event import dehydrate_event


def dehydrate_events(
    events: list[Event],
    pool: FileInfoPool,
) -> tuple[list[Event], FileInfoPool]:
    dehydrated = False
    new_events: list[Event] = []

    for event in events:
        new_event, pool = dehydrate_event(event, pool)

        if new_event is not event:
            dehydrated = True

        new_events.append(new_event)

    if not dehydrated:
        return events, pool
    else:
        return new_events, pool
