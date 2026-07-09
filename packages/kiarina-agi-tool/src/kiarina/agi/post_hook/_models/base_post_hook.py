from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.event import Event

from .._schemas.post_hook_context import PostHookContext
from .._types.post_hook import PostHook
from .._types.post_hook_name import PostHookName


class BasePostHook(PostHook):
    def __init__(
        self,
        hook_config: dict[str, Any] | None = None,
    ) -> None:
        self.hook_config: dict[str, Any] = hook_config or {}
        self._name: PostHookName | None = None

    @property
    def name(self) -> PostHookName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Hook name not set")

        return self._name

    @name.setter
    def name(self, value: PostHookName) -> None:
        self._name = value

    async def run(self, ctx: PostHookContext) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield
        return

    def __str__(self) -> str:
        return self.__class__.__name__
