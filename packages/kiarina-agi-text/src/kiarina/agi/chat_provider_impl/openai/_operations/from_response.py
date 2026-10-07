from typing import TYPE_CHECKING

from kiarina.agi.message import AIMessage, ToolCall

from .._exceptions.openai_response_error import OpenAIResponseError
from .._schemas.openai_chat_result import OpenAIChatResult
from .._schemas.openai_usage import OpenAIUsage
from .._types.openai_stop_reason import OpenAIStopReason
from .parse_tool_call_args import parse_tool_call_args

if TYPE_CHECKING:
    from openai.types.responses import Response


def from_response(response: "Response") -> OpenAIChatResult:
    """Reasoning items are dropped because requests are sent with `store=False`."""
    if response.status == "failed":
        error = response.error
        detail = f"{error.code}: {error.message}" if error else "unknown error"
        raise OpenAIResponseError(f"Response failed: {detail}")

    texts: list[str] = []
    tool_calls: list[ToolCall] = []

    for item in response.output:
        if item.type == "message":
            for content in item.content:
                if content.type == "output_text":
                    texts.append(content.text or "")
                elif content.type == "refusal":
                    texts.append(content.refusal)

        elif item.type == "function_call":
            tool_calls.append(
                ToolCall(
                    id=item.call_id,
                    name=item.name,
                    args=parse_tool_call_args(item.arguments),
                )
            )

    return OpenAIChatResult(
        ai_message=AIMessage.create(text="".join(texts), tool_calls=tool_calls),
        stop_reason=_to_stop_reason(response),
        usage=_to_usage(response),
    )


def _to_stop_reason(response: "Response") -> OpenAIStopReason:
    if response.status != "incomplete" or not response.incomplete_details:
        return "stop"

    if response.incomplete_details.reason == "max_output_tokens":
        return "max_tokens"

    if response.incomplete_details.reason == "content_filter":
        return "content_filter"

    return "stop"


def _to_usage(response: "Response") -> OpenAIUsage | None:
    usage = response.usage

    if usage is None:
        return None

    return OpenAIUsage(
        prompt_tokens=usage.input_tokens,
        cached_input_tokens=usage.input_tokens_details.cached_tokens,
        cache_write_tokens=usage.input_tokens_details.cache_write_tokens,
        output_tokens=usage.output_tokens,
    )
