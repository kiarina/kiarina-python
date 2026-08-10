from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event

from .._schemas.post_hook_context import PostHookContext
from .post_hook_name import PostHookName


@runtime_checkable
class PostHook(Protocol):
    name: PostHookName

    def run(self, ctx: PostHookContext) -> AsyncIterator[Event]: ...
