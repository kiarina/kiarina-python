from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.event import Event

from .._schemas.pre_hook_context import PreHookContext
from .._types.pre_hook import PreHook
from .._types.pre_hook_name import PreHookName


class BasePreHook(PreHook):
    def __init__(
        self,
        hook_config: dict[str, Any] | None = None,
    ) -> None:
        self.hook_config: dict[str, Any] = hook_config or {}
        self._name: PreHookName | None = None

    @property
    def name(self) -> PreHookName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Hook name not set")

        return self._name

    @name.setter
    def name(self, value: PreHookName) -> None:
        self._name = value

    async def run(self, ctx: PreHookContext) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield
        return

    def __str__(self) -> str:
        return self.__class__.__name__
