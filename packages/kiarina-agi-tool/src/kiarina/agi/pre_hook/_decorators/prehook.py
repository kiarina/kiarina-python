import inspect
from collections.abc import AsyncIterator, Callable
from typing import overload

from kiarina.agi.event import Event

from .._models.base_pre_hook import BasePreHook
from .._schemas.pre_hook_context import PreHookContext
from .._types.pre_hook_output import PreHookOutput


@overload
def prehook(
    func: Callable[[PreHookContext], PreHookOutput],
) -> type[BasePreHook]: ...


@overload
def prehook() -> Callable[
    [Callable[[PreHookContext], PreHookOutput]],
    type[BasePreHook],
]: ...


def prehook(
    func: Callable[[PreHookContext], PreHookOutput] | None = None,
) -> (
    type[BasePreHook]
    | Callable[
        [Callable[[PreHookContext], PreHookOutput]],
        type[BasePreHook],
    ]
):
    def _create_pre_hook_class(
        func: Callable[[PreHookContext], PreHookOutput],
    ) -> type[BasePreHook]:
        class PreHookClass(BasePreHook):
            async def run(self, ctx: PreHookContext) -> AsyncIterator[Event]:
                result = func(ctx)

                if inspect.isasyncgen(result):
                    async for event in result:
                        yield event
                elif inspect.isawaitable(result):
                    await result
                else:
                    return

        PreHookClass.__name__ = func.__name__
        PreHookClass.__qualname__ = func.__qualname__
        PreHookClass.__module__ = func.__module__
        PreHookClass.__doc__ = func.__doc__

        return PreHookClass

    if func is not None:
        return _create_pre_hook_class(func)

    return _create_pre_hook_class
