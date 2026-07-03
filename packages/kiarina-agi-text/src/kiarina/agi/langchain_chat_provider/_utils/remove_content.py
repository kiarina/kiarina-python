from typing import TypeVar

from .._types.lc_base_message import LCBaseMessage

T = TypeVar("T", bound=LCBaseMessage)


def remove_content(message: T, content_type: str) -> T:
    if isinstance(message.content, str):
        return message

    new_content: list[str | dict[str, object]] = []

    for content in message.content:
        if isinstance(content, str):
            new_content.append(content)
        elif content.get("type") != content_type:
            new_content.append(content)

    if len(new_content) == len(message.content):
        return message
    else:
        return message.model_copy(update={"content": new_content})
