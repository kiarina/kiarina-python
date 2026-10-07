from dataclasses import dataclass

from kiarina.agi.message import AIMessage

from .._types.openai_stop_reason import OpenAIStopReason
from .openai_usage import OpenAIUsage


@dataclass
class OpenAIChatResult:
    ai_message: AIMessage
    stop_reason: OpenAIStopReason = "stop"
    usage: OpenAIUsage | None = None
