from typing import cast

from kiarina.agi.chat_content import ContentPart


def to_openai_parts(
    parts: list[ContentPart], *, text_type: str = "text"
) -> str | list[str | ContentPart]:
    """
    Drop `cache_control`, which OpenAI does not accept, rename text parts to
    `text_type`, and collapse a single text part into a string.
    """
    openai_parts: list[ContentPart] = []

    for part in parts:
        part = {k: v for k, v in part.items() if k != "cache_control"}

        if part.get("type") == "text":
            part["type"] = text_type

        openai_parts.append(part)

    if not openai_parts:
        return ""

    if (
        len(openai_parts) == 1
        and openai_parts[0].get("type") == text_type
        and isinstance(openai_parts[0].get("text"), str)
    ):
        return str(openai_parts[0]["text"])

    return cast(list[str | ContentPart], openai_parts)
