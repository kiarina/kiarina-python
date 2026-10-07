from dataclasses import dataclass, field
from typing import Any


@dataclass
class CodexRequest:
    instructions: str | None = None
    """The leading system messages, sent as the thread's base instructions."""

    items: list[dict[str, Any]] = field(default_factory=list)
    """The rest of the conversation as raw Responses API items."""

    item_ends: list[int] = field(default_factory=list)
    """For each message, the number of items up to and including it."""

    instruction_item: dict[str, Any] | None = None
    """A developer message asking for a forced tool choice, sent after the conversation."""

    @property
    def injected_items(self) -> list[dict[str, Any]]:
        """The items to inject into a new thread."""
        if self.instruction_item:
            return [*self.items, self.instruction_item]

        return self.items
