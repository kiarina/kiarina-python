from collections.abc import AsyncIterator, Awaitable
from typing import TypeAlias

from kiarina.agi.event import Event

PreHookOutput: TypeAlias = Awaitable[None] | AsyncIterator[Event] | None
