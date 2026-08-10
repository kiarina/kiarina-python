from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from .._schemas.state_context import StateContext
from .state_name import StateName


@runtime_checkable
class State(Protocol):
    def run(
        self,
        state_context: StateContext,
    ) -> AsyncIterator[Event | StateName | None]: ...
