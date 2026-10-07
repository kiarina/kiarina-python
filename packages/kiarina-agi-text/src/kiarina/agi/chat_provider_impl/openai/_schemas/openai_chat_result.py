from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.message import AIMessage

from .._types.openai_stop_reason import OpenAIStopReason
from .openai_usage import OpenAIUsage


@dataclass
class OpenAIChatResult:
    ai_message: AIMessage
    stop_reason: OpenAIStopReason = "stop"
    usage: OpenAIUsage | None = None
    reasoning_items: list[dict[str, Any]] = field(default_factory=list)
    """Encrypted reasoning items of the Responses API, to send back with this turn."""
