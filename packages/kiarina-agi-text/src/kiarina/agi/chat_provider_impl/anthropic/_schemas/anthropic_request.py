from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnthropicRequest:
    system: str | list[dict[str, Any]] | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
