from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.message import AIMessage


@dataclass
class ClaudeAgentSDKChatResult:
    ai_message: AIMessage

    stop_reason: str | None = None

    usage: dict[str, Any] = field(default_factory=dict)

    total_cost_usd: float | None = None
    """What the request would cost on the API. A subscription is not billed per request."""
