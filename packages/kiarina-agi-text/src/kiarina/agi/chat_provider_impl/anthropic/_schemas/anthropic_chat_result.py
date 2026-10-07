from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.message import AIMessage

from .._types.anthropic_stop_reason import AnthropicStopReason
from .anthropic_usage import AnthropicUsage


@dataclass
class AnthropicChatResult:
    ai_message: AIMessage
    stop_reason: AnthropicStopReason = "stop"
    usage: AnthropicUsage | None = None
    thinking_blocks: list[dict[str, Any]] = field(default_factory=list)
    """`thinking` and `redacted_thinking` blocks, to send back with this turn."""
