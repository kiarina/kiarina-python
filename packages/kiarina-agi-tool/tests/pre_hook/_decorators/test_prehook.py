from collections.abc import AsyncIterator

from kiarina.agi.event import CustomEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.pre_hook import BasePreHook, PreHookContext, prehook
from kiarina.agi.run_context import RunContext


def test_prehook_sync() -> None:
    @prehook
    def SyncPreHook(ctx: PreHookContext) -> None:
        return None

    assert issubclass(SyncPreHook, BasePreHook)
    assert SyncPreHook.__name__ == "SyncPreHook"


async def test_prehook_async(run_context: RunContext) -> None:
    @prehook
    async def AsyncPreHook(ctx: PreHookContext) -> None:
        return None

    hook = AsyncPreHook()
    hook.name = "async"
    ctx = PreHookContext.create(
        tool_call=ToolCall(name="run", id="call-1"), run_context=run_context
    )

    events = [event async for event in hook.run(ctx)]
    assert events == []


async def test_prehook_async_iterator(run_context: RunContext) -> None:
    @prehook
    async def IteratorPreHook(ctx: PreHookContext) -> AsyncIterator[CustomEvent]:
        yield CustomEvent(payload={"type": "prehook"})

    hook = IteratorPreHook()
    hook.name = "iter"
    ctx = PreHookContext.create(
        tool_call=ToolCall(name="run", id="call-1"), run_context=run_context
    )

    events = [event async for event in hook.run(ctx)]
    assert len(events) == 1
    assert isinstance(events[0], CustomEvent)
    assert events[0].payload == {"type": "prehook"}
