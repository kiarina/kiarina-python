from collections.abc import AsyncIterator, Iterator

import pytest

from kiarina.agi.event import CustomEvent, Event, ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.post_hook import (
    BasePostHook,
    PostHookContext,
    run_post_hooks,
    settings_manager,
)
from kiarina.agi.run_context import RunContext


class MyPostHook(BasePostHook):
    async def run(self, ctx: PostHookContext) -> AsyncIterator[Event]:
        yield CustomEvent(payload={"type": "post", "event_count": len(ctx.events)})


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "customs": {"my": f"{__name__}:MyPostHook"},
    }
    yield
    settings_manager.cli_args = {}


async def test_run_post_hooks(run_context: RunContext) -> None:
    hook = MyPostHook()
    hook.name = "inline"

    tool_events: list[Event] = [
        ToolMessageEvent.create(
            "Hello",
            tool_name="run",
            tool_call_id="call-1",
        ),
    ]

    events = [
        event
        async for event in run_post_hooks(
            ToolCall(name="run", args={}, id="call-1"),
            tool_events,
            hooks=[hook, "my"],
            run_context=run_context,
        )
    ]

    assert len(events) == 2
    assert isinstance(events[0], CustomEvent)
    assert isinstance(events[1], CustomEvent)
    assert events[0].payload == {"type": "post", "event_count": 1}
    assert events[1].payload == {"type": "post", "event_count": 1}
