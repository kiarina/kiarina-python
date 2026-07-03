from kiarina.agi.data.content import Content, dehydrate_content
from kiarina.agi.data.file_info_pool import FileInfoPool

from .._types.message import Message


def dehydrate_message(
    message: Message,
    pool: FileInfoPool,
) -> tuple[Message, FileInfoPool]:
    dehydrated = False
    new_contents: list[Content] = []

    for content in message.contents:
        new_content, pool = dehydrate_content(content, pool)

        if new_content is not content:
            dehydrated = True

        new_contents.append(new_content)

    if not dehydrated:
        return message, pool

    new_message = message.model_copy(update={"contents": new_contents})
    return new_message, pool
