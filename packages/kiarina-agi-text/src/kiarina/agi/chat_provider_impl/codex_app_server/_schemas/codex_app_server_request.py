from dataclasses import dataclass, field
from typing import Any


@dataclass
class CodexAppServerRequest:
    instructions: str | None = None
    """The leading system messages, sent as the thread's base instructions."""

    items: list[dict[str, Any]] = field(default_factory=list)
    """The rest of the conversation as raw Responses API items."""
