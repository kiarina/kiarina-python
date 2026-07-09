from collections.abc import AsyncIterator

from kiarina.agi.event import Event
from kiarina.agi.post_hook import BasePostHook, PostHookContext


class DummyPostHook(BasePostHook):
    pass


class ErrorPostHook(BasePostHook):
    async def run(self, ctx: PostHookContext) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield


def test_base_post_hook() -> None:
    hook = DummyPostHook()
    hook.name = "dummy"

    print("hook_name:", hook.name)
    print("__str__:", str(hook))
