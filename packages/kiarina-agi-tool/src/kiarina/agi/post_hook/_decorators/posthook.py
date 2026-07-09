import inspect
from collections.abc import AsyncIterator, Callable
from typing import overload

from kiarina.agi.event import Event

from .._models.base_post_hook import BasePostHook
from .._schemas.post_hook_context import PostHookContext
from .._types.post_hook_output import PostHookOutput


@overload
def posthook(
    func: Callable[[PostHookContext], PostHookOutput],
) -> type[BasePostHook]: ...


@overload
def posthook() -> Callable[
    [Callable[[PostHookContext], PostHookOutput]],
    type[BasePostHook],
]: ...


def posthook(
    func: Callable[[PostHookContext], PostHookOutput] | None = None,
) -> (
    type[BasePostHook]
    | Callable[
        [Callable[[PostHookContext], PostHookOutput]],
        type[BasePostHook],
    ]
):
    def _create_post_hook_class(
        func: Callable[[PostHookContext], PostHookOutput],
    ) -> type[BasePostHook]:
        class PostHookClass(BasePostHook):
            async def run(self, ctx: PostHookContext) -> AsyncIterator[Event]:
                result = func(ctx)

                if inspect.isasyncgen(result):
                    async for event in result:
                        yield event
                elif inspect.isawaitable(result):
                    await result
                else:
                    return

        PostHookClass.__name__ = func.__name__
        PostHookClass.__qualname__ = func.__qualname__
        PostHookClass.__module__ = func.__module__
        PostHookClass.__doc__ = func.__doc__

        return PostHookClass

    if func is not None:
        return _create_post_hook_class(func)

    return _create_post_hook_class
