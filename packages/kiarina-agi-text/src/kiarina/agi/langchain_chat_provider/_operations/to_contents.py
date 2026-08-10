from kiarina.agi.content import Content

from .._types.lc_content import LCContent


def to_contents(lc_content: str | list[str | LCContent]) -> list[Content]:
    if isinstance(lc_content, str):
        return [Content(text=lc_content)]

    contents: list[Content] = []

    for item in lc_content:
        if isinstance(item, str):
            contents.append(Content(text=item))
        elif isinstance(item, dict):
            if item.get("type") == "text":
                contents.append(Content(text=item.get("text", "")))
            else:
                contents.append(Content(payload=item))
        else:
            raise ValueError(f"Unsupported content type: {type(item)}")

    return contents
