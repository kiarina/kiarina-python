from typing import TypeVar

from .._types.lc_base_message import LCBaseMessage

T = TypeVar("T", bound=LCBaseMessage)


def normalize_content(message: T) -> T:
    if isinstance(message.content, str) or len(message.content) > 1:
        return message

    if not message.content:
        return message.model_copy(update={"content": ""})

    content_item = message.content[0]

    if isinstance(content_item, str):
        return message.model_copy(update={"content": content_item})

    if content_item.get("type") == "text":
        return message.model_copy(update={"content": content_item["text"]})

    return message
