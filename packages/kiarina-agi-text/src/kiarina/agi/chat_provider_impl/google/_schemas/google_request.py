from dataclasses import dataclass, field
from typing import Any


@dataclass
class GoogleRequest:
    system_instruction: str | None = None
    contents: list[Any] = field(default_factory=list)
    """`google.genai.types.Content` items."""
