from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """A source of the current time. `now()` returns a timezone-aware datetime."""

    def now(self) -> datetime: ...
