from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from .._schemas.pre_hook_context import PreHookContext
from .pre_hook_name import PreHookName


@runtime_checkable
class PreHook(Protocol):
    name: PreHookName

    def run(self, ctx: PreHookContext) -> AsyncIterator[Event]: ...
