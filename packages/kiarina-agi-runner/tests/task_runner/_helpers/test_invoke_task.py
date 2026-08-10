from kiarina.agi.event import AIMessageEvent
from kiarina.agi.run_context import RunContext
from kiarina.agi.task_runner import invoke_task


async def test_invoke_task(run_context: RunContext) -> None:
    events = [e async for e in invoke_task("Hello", run_context=run_context)]

    assert len(events) == 1
    assert isinstance(events[0], AIMessageEvent)
