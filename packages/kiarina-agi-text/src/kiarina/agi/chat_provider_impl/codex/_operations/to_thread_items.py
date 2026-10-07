import json
from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter, from_contents
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice

from .._schemas.codex_request import CodexRequest


async def to_thread_items(
    messages: list[Message],
    *,
    tool_choice: ToolChoice | None,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> CodexRequest:
    """
    Convert messages into raw Responses API items for `thread/inject_items`.

    The whole conversation is injected, the last message included, and the turn
    starts with no input. GPT-6 writes the cache at the end of the latest
    message only, so the next request, which repeats these items and appends
    more, finds the cache only if the last item comes back unchanged.

    Codex always sends `tool_choice: auto`, so a forced tool choice is asked for
    in a developer message after the conversation (`instruction_item`).
    """
    request = CodexRequest()
    systems: list[str] = []

    for message in messages:
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )

        if message.type == "system":
            text = _to_text(result.parts)

            if not request.items:
                systems.append(text)
            else:
                request.items.append(_message("developer", result.parts))

        elif message.type == "human":
            request.items.append(_message("user", result.parts))

        elif message.type == "ai":
            if text := _to_text(result.parts):
                request.items.append(
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": text}],
                    }
                )

            for tool_call in message.tool_calls:
                request.items.append(
                    {
                        "type": "function_call",
                        "call_id": tool_call.id,
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.args, ensure_ascii=False),
                    }
                )

        elif message.type == "tool":
            request.items.append(
                {
                    "type": "function_call_output",
                    "call_id": message.tool_call_id,
                    "output": _to_output(result.parts),
                }
            )

            if result.purged_parts:
                request.items.append(_message("user", result.purged_parts))

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

        request.item_ends.append(len(request.items))

    if tool_choice == "any":
        instruction = "You must respond by calling one of the provided tools."
    elif tool_choice is not None and tool_choice != "auto":
        instruction = f"You must respond by calling the `{tool_choice}` tool."
    else:
        instruction = None

    if instruction:
        request.instruction_item = _message(
            "developer", [{"type": "text", "text": instruction}]
        )

    request.instructions = "\n\n".join(s for s in systems if s) or None
    return request


def _to_text(parts: list[ContentPart]) -> str:
    return "\n\n".join(
        str(part.get("text") or "") for part in parts if part.get("type") == "text"
    ).strip()


def _to_content(parts: list[ContentPart]) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = []

    for part in parts:
        if part.get("type") == "text":
            if text := str(part.get("text") or ""):
                content.append({"type": "input_text", "text": text})
        else:
            content.append({k: v for k, v in part.items() if k != "cache_control"})

    return content or [{"type": "input_text", "text": "<no message>"}]


def _message(role: str, parts: list[ContentPart]) -> dict[str, Any]:
    return {"type": "message", "role": role, "content": _to_content(parts)}


def _to_output(parts: list[ContentPart]) -> str | list[dict[str, Any]]:
    content = _to_content(parts)

    if len(content) == 1 and content[0]["type"] == "input_text":
        return str(content[0]["text"])

    return content
