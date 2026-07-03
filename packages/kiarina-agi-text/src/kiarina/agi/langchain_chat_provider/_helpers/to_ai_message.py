from kiarina.agi.content import Content
from kiarina.agi.message import AIMessage, ToolCall

from .._types.lc_ai_message import LCAIMessage
from .._types.lc_content import LCContent
from .._types.lc_tool_call import LCToolCall


def to_ai_message(lc_ai_message: LCAIMessage) -> AIMessage:
    return AIMessage(
        contents=_to_contents(lc_ai_message.content),
        tool_calls=_to_tool_calls(lc_ai_message.tool_calls),
    )


def _to_contents(lc_content: str | list[str | LCContent]) -> list[Content]:
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


def _to_tool_calls(lc_tool_calls: list[LCToolCall]) -> list[ToolCall]:
    tool_calls: list[ToolCall] = []

    for lc_tool_call in lc_tool_calls:
        tool_calls.append(
            ToolCall(
                id=lc_tool_call.get("id") or "",
                name=lc_tool_call.get("name") or "",
                args=lc_tool_call.get("args") or {},
            )
        )

    return tool_calls
