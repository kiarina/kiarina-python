from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.event import Event

from .._schemas.state_context import StateContext
from .._types.state import State
from .._types.state_name import StateName


class BaseState(State, ABC):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs

    @abstractmethod
    async def run(
        self,
        ctx: StateContext,
    ) -> AsyncIterator[Event | StateName | None]:
        yield None
