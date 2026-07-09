from collections.abc import AsyncIterator

from kiarina.agi.event import Event
from kiarina.agi.pre_hook import BasePreHook, PreHookContext


class DummyPreHook(BasePreHook):
    pass


class ErrorPreHook(BasePreHook):
    async def run(self, ctx: PreHookContext) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield


def test_base_pre_hook() -> None:
    hook = DummyPreHook()
    hook.name = "dummy"

    print("hook_name:", hook.name)
    print("__str__:", str(hook))
