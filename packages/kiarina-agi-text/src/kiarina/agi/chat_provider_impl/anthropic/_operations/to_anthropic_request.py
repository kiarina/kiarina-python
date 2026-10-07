from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter, from_contents
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .._constants.mid_conversation_system_model_prefixes import (
    MID_CONVERSATION_SYSTEM_MODEL_PREFIXES,
)
from .._schemas.anthropic_request import AnthropicRequest

_EMPTY_TEXT = "<no message>"


async def to_anthropic_request(
    messages: list[Message],
    *,
    model_name: str,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> AnthropicRequest:
    """
    Convert messages into Anthropic's `system` and `messages`.

    - The leading system message becomes `system`. A later one stays in place as a
      `system` turn when the model supports it and it comes before an assistant turn
      or at the end; otherwise it is moved to `system`.
    - Consecutive human and tool messages are merged into one user turn, because
      tool results must sit together in the turn after the tool use.
    """
    request = AnthropicRequest()
    pending_systems: list[str | list[dict[str, Any]]] = []
    supports_mid_system = model_name.startswith(MID_CONVERSATION_SYSTEM_MODEL_PREFIXES)

    for index, message in enumerate(messages):
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )

        if message.type == "system":
            system = _to_system(result.parts)

            if index == 0:
                request.system = system
            elif supports_mid_system and (
                pending_systems or _last_role(request) == "user"
            ):
                pending_systems.append(system)
            else:
                _hoist_system(request, system)

            continue

        if message.type == "ai":
            content = _to_blocks(result.parts, allow_empty=True)
            content += [
                {
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "input": tool_call.args,
                }
                for tool_call in message.tool_calls
            ]

            if pending_systems:
                request.messages += [
                    {"role": "system", "content": system} for system in pending_systems
                ]
                pending_systems.clear()

            request.messages.append(
                {"role": "assistant", "content": content or _empty_blocks()}
            )
            continue

        for system in pending_systems:
            _hoist_system(request, system)

        pending_systems.clear()

        if message.type == "human":
            blocks = _to_blocks(result.parts)

        elif message.type == "tool":
            tool_result = _to_tool_result(
                message.tool_call_id, result.parts, failed=message.failed
            )
            blocks = [tool_result]

            if result.purged_parts:
                blocks += _to_blocks(result.purged_parts)

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

        if _last_role(request) == "user":
            request.messages[-1]["content"] += blocks
        else:
            request.messages.append({"role": "user", "content": blocks})

    request.messages += [
        {"role": "system", "content": system} for system in pending_systems
    ]

    _strip_final_assistant_text(request)
    return request


def _last_role(request: AnthropicRequest) -> str | None:
    return request.messages[-1]["role"] if request.messages else None


def _hoist_system(
    request: AnthropicRequest, system: str | list[dict[str, Any]]
) -> None:
    if request.system is not None:
        raise ValueError("Received multiple non-consecutive system messages.")

    request.system = system


def _to_system(parts: list[ContentPart]) -> str | list[dict[str, Any]]:
    blocks = [part for part in parts if part.get("type") == "text"]

    if len(blocks) == 1 and "cache_control" not in blocks[0]:
        return str(blocks[0].get("text") or _EMPTY_TEXT)

    return blocks or _EMPTY_TEXT


def _to_blocks(
    parts: list[ContentPart], *, allow_empty: bool = False
) -> list[dict[str, Any]]:
    blocks = [
        part
        for part in parts
        if part.get("type") != "text" or str(part.get("text") or "").strip()
    ]

    if not blocks and not allow_empty:
        return _empty_blocks()

    return blocks


def _empty_blocks() -> list[dict[str, Any]]:
    return [{"type": "text", "text": _EMPTY_TEXT}]


def _to_tool_result(
    tool_use_id: str, parts: list[ContentPart], *, failed: bool
) -> dict[str, Any]:
    """`cache_control` is not allowed inside a tool result, so it is lifted to it."""
    cache_control: dict[str, Any] | None = None
    content: list[dict[str, Any]] = []

    for part in _to_blocks(parts):
        if "cache_control" in part:
            cache_control = part["cache_control"]
            part = {k: v for k, v in part.items() if k != "cache_control"}

        content.append(part)

    tool_result: dict[str, Any] = {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": content,
    }

    if failed:
        tool_result["is_error"] = True

    if cache_control:
        tool_result["cache_control"] = cache_control

    return tool_result


def _strip_final_assistant_text(request: AnthropicRequest) -> None:
    """The API rejects trailing whitespace in a final assistant turn."""
    if _last_role(request) != "assistant":
        return

    content = request.messages[-1]["content"]

    if content and content[-1].get("type") == "text":
        content[-1] = {**content[-1], "text": content[-1]["text"].rstrip()}
