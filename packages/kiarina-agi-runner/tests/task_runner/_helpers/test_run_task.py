from kiarina.agi.event import AIMessageEvent
from kiarina.agi.run_context import RunContext
from kiarina.agi.task_runner import run_task


async def test_run_task(run_context: RunContext) -> None:
    events = [
        e
        async for e in run_task(
            "Hello", tool_options={"tools": ["hello"]}, run_context=run_context
        )
    ]

    assert len(events) == 1
    assert isinstance(events[0], AIMessageEvent)
