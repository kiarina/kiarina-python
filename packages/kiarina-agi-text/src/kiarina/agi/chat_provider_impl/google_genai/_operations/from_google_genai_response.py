import uuid
from typing import Any

from kiarina.agi.message import AIMessage, ToolCall

from .._schemas.google_genai_chat_result import GoogleGenAIChatResult
from .from_finish_reason import from_finish_reason
from .from_usage_metadata import from_usage_metadata


def from_google_genai_response(
    response: Any, *, tool_call_ids: dict[int, str] | None = None
) -> GoogleGenAIChatResult:
    """
    Take a `GenerateContentResponse`. Thought parts are dropped. A function call
    without an id gets one, or the id from `tool_call_ids` by its position, so a
    stream and its final result agree.
    """
    texts: list[str] = []
    tool_calls: list[ToolCall] = []
    finish_reason: str | None = None
    candidates = response.candidates or []

    if candidates:
        candidate = candidates[0]
        finish_reason = _enum_name(candidate.finish_reason)
        parts = candidate.content.parts if candidate.content else None

        for part in parts or []:
            if part.function_call:
                position = len(tool_calls)
                tool_calls.append(
                    ToolCall(
                        id=part.function_call.id
                        or (tool_call_ids or {}).get(position)
                        or str(uuid.uuid4()),
                        name=part.function_call.name or "",
                        args=dict(part.function_call.args or {}),
                    )
                )
            elif part.text and not part.thought:
                texts.append(part.text)

    prompt_feedback = response.prompt_feedback

    return GoogleGenAIChatResult(
        ai_message=AIMessage.create(text="".join(texts), tool_calls=tool_calls),
        stop_reason=from_finish_reason(
            finish_reason,
            prompt_blocked=bool(prompt_feedback and prompt_feedback.block_reason),
        ),
        usage=from_usage_metadata(response.usage_metadata),
    )


def _enum_name(value: Any) -> str | None:
    if value is None:
        return None

    return str(getattr(value, "name", value))
