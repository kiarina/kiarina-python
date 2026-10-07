import json
from typing import Any

from kiarina.agi.content import Content
from kiarina.agi.message import AIMessage, ToolCall

from .._schemas.codex_chat_result import CodexChatResult


def from_raw_response_items(
    items: list[dict[str, Any]], usage: dict[str, Any] | None
) -> CodexChatResult:
    """
    Build the model turn from the Responses API items of one response.
    The user's own message item and reasoning items are dropped.
    """
    texts: list[str] = []
    tool_calls: list[ToolCall] = []

    for item in items:
        if item.get("type") == "message" and item.get("role") == "assistant":
            texts += [
                str(part.get("text") or "")
                for part in item.get("content") or []
                if part.get("type") == "output_text"
            ]
        elif item.get("type") == "function_call":
            tool_calls.append(
                ToolCall(
                    id=item["call_id"],
                    name=item["name"],
                    args=_parse_arguments(item.get("arguments")),
                )
            )

    return CodexChatResult(
        ai_message=AIMessage(
            contents=[Content(text="".join(texts))], tool_calls=tool_calls
        ),
        usage=usage or {},
    )


def _parse_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments

    if not arguments:
        return {}

    parsed = json.loads(arguments)
    return parsed if isinstance(parsed, dict) else {}
