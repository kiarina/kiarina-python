from .._types.lc_message import LCMessage


def has_content(lc_messages: list[LCMessage], content_type: str) -> bool:
    for lc_message in lc_messages:
        if isinstance(lc_message.content, str):
            continue

        for content in lc_message.content:
            if isinstance(content, str):
                continue

            if content.get("type") == content_type:
                return True

    return False
