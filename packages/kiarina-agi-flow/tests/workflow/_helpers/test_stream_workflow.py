from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.workflow import stream_workflow


async def test_stream_workflow(history: History, run_context: RunContext) -> None:
    events = [
        event
        async for event in stream_workflow(
            history,
            run_context=run_context,
        )
    ]

    assert len(events) > 0
    assert events[-1].type == "ai_message"
