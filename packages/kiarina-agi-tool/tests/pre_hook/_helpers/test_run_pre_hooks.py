from collections.abc import AsyncIterator, Iterator

import pytest

from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.message import ToolCall
from kiarina.agi.pre_hook import (
    BasePreHook,
    PreHookContext,
    run_pre_hooks,
    settings_manager,
)
from kiarina.agi.run_context import RunContext


class MyPreHook(BasePreHook):
    async def run(self, ctx: PreHookContext) -> AsyncIterator[Event]:
        yield CustomEvent(payload={"type": "pre", "tool_name": ctx.tool_call.name})


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "customs": {"my": f"{__name__}:MyPreHook"},
    }
    yield
    settings_manager.cli_args = {}


async def test_run_pre_hooks(run_context: RunContext) -> None:
    hook = MyPreHook()
    hook.name = "inline"

    events = [
        event
        async for event in run_pre_hooks(
            ToolCall(name="run", args={}, id="call-1"),
            hooks=[hook, "my"],
            run_context=run_context,
        )
    ]

    assert len(events) == 2
    assert isinstance(events[0], CustomEvent)
    assert isinstance(events[1], CustomEvent)
    assert events[0].payload == {"type": "pre", "tool_name": "run"}
    assert events[1].payload == {"type": "pre", "tool_name": "run"}
