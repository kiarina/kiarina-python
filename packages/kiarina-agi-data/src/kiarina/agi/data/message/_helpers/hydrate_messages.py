from kiarina.agi.data.content import Content, hydrate_content
from kiarina.agi.data.file_info_pool import FileInfoPool

from .._types.message import Message


def hydrate_messages(
    messages: list[Message],
    pool: FileInfoPool,
) -> tuple[list[Message], FileInfoPool]:
    hydrated = False
    new_messages: list[Message] = []

    for message in messages:
        new_message, pool = _hydrate_message(message, pool)

        if new_message is not message:
            hydrated = True

        new_messages.append(new_message)

    if not hydrated:
        return messages, pool

    return new_messages, pool


def _hydrate_message(
    message: Message,
    pool: FileInfoPool,
) -> tuple[Message, FileInfoPool]:
    hydrated = False
    new_contents: list[Content] = []

    for content in message.contents:
        new_content, pool = hydrate_content(content, pool)

        if new_content is not content:
            hydrated = True

        new_contents.append(new_content)

    if not hydrated:
        return message, pool

    new_message = message.model_copy(update={"contents": new_contents})
    return new_message, pool
