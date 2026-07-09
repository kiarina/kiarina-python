from collections.abc import AsyncIterator, Awaitable
from typing import TypeAlias

from kiarina.agi.event import Event

PostHookOutput: TypeAlias = None | Awaitable[None] | AsyncIterator[Event]
