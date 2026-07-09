from collections.abc import AsyncIterator

from kiarina.agi.event import CustomEvent, ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.post_hook import BasePostHook, PostHookContext, posthook
from kiarina.agi.run_context import RunContext


def test_posthook_sync() -> None:
    @posthook
    def SyncPostHook(ctx: PostHookContext) -> None:
        return None

    assert issubclass(SyncPostHook, BasePostHook)
    assert SyncPostHook.__name__ == "SyncPostHook"


async def test_posthook_async(run_context: RunContext) -> None:
    @posthook
    async def AsyncPostHook(ctx: PostHookContext) -> None:
        return None

    hook = AsyncPostHook()
    hook.name = "async"
    ctx = PostHookContext.create(
        tool_call=ToolCall(name="run", id="call-1"),
        events=[
            ToolMessageEvent.create(
                "ok",
                tool_name="run",
                tool_call_id="call-1",
            )
        ],
        run_context=run_context,
    )

    events = [event async for event in hook.run(ctx)]
    assert events == []


async def test_posthook_async_iterator(run_context: RunContext) -> None:
    @posthook
    async def IteratorPostHook(ctx: PostHookContext) -> AsyncIterator[CustomEvent]:
        yield CustomEvent(payload={"type": "posthook"})

    hook = IteratorPostHook()
    hook.name = "iter"
    ctx = PostHookContext.create(
        tool_call=ToolCall(name="run", id="call-1"),
        events=[
            ToolMessageEvent.create(
                "ok",
                tool_call_id="call-1",
                tool_name="run",
            )
        ],
        run_context=run_context,
    )

    events = [event async for event in hook.run(ctx)]
    assert len(events) == 1
    assert isinstance(events[0], CustomEvent)
    assert events[0].payload == {"type": "posthook"}
