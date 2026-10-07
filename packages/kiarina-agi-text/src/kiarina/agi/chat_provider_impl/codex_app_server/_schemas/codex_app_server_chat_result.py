from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.message import AIMessage


@dataclass
class CodexAppServerChatResult:
    ai_message: AIMessage

    usage: dict[str, Any] = field(default_factory=dict)
    """`TokenUsageBreakdown` of the response. `inputTokens` includes the cached tokens."""
