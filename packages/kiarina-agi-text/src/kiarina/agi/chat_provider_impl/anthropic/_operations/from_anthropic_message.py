from typing import TYPE_CHECKING, Any

from kiarina.agi.message import AIMessage, ToolCall

from .._schemas.anthropic_chat_result import AnthropicChatResult
from .._types.cache_ttl import CacheTTL
from .from_anthropic_usage import from_anthropic_usage
from .from_stop_reason import from_stop_reason

if TYPE_CHECKING:
    from anthropic.types import Message


def from_anthropic_message(
    message: "Message", *, cache_ttl: CacheTTL
) -> AnthropicChatResult:
    texts: list[str] = []
    tool_calls: list[ToolCall] = []
    thinking_blocks: list[dict[str, Any]] = []

    for block in message.content:
        if block.type in ("thinking", "redacted_thinking"):
            thinking_blocks.append(block.model_dump(mode="json", exclude_none=True))
        elif block.type == "text":
            texts.append(block.text)
        elif block.type == "tool_use":
            tool_calls.append(
                ToolCall(
                    id=block.id,
                    name=block.name,
                    args=block.input if isinstance(block.input, dict) else {},
                )
            )

    return AnthropicChatResult(
        ai_message=AIMessage.create(text="".join(texts), tool_calls=tool_calls),
        stop_reason=from_stop_reason(message.stop_reason),
        usage=from_anthropic_usage(message.usage, cache_ttl=cache_ttl),
        thinking_blocks=thinking_blocks,
    )
