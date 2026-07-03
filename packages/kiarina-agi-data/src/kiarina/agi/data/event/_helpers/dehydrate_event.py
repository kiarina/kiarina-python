from kiarina.agi.data.file_info_pool import FileInfoPool
from kiarina.agi.data.message import dehydrate_message

from .._types.event import Event


def dehydrate_event(
    event: Event,
    pool: FileInfoPool,
) -> tuple[Event, FileInfoPool]:
    if event.type == "custom":
        return event, pool
    elif event.type == "ai_message_chunk":  # pragma: no cover
        return event, pool
    else:
        new_message, pool = dehydrate_message(event.message, pool)

        if new_message is event.message:
            return event, pool

        new_event = event.model_copy(update={"message": new_message})
        return new_event, pool
