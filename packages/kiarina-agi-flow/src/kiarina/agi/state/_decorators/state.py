from collections.abc import AsyncIterator, Callable

from kiarina.agi.event import Event

from .._models.base_state import BaseState
from .._schemas.state_context import StateContext
from .._types.state_name import StateName


def state(
    func: Callable[..., AsyncIterator[Event | StateName | None]],
) -> type[BaseState]:
    class StateClass(BaseState):
        async def run(
            self,
            ctx: StateContext,
        ) -> AsyncIterator[Event | StateName | None]:
            async for item in func(ctx, **self.init_kwargs):
                yield item

    StateClass.__name__ = func.__name__
    StateClass.__qualname__ = func.__qualname__
    StateClass.__module__ = func.__module__
    StateClass.__doc__ = func.__doc__

    return StateClass
