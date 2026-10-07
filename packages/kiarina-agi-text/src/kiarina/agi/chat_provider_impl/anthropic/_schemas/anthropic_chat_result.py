from dataclasses import dataclass

from kiarina.agi.message import AIMessage

from .._types.anthropic_stop_reason import AnthropicStopReason
from .anthropic_usage import AnthropicUsage


@dataclass
class AnthropicChatResult:
    ai_message: AIMessage
    stop_reason: AnthropicStopReason = "stop"
    usage: AnthropicUsage | None = None
