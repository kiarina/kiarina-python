from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.workflow import invoke_workflow


async def test_invoke_workflow(history: History, run_context: RunContext) -> None:
    events = [
        event
        async for event in invoke_workflow(
            history,
            run_context=run_context,
        )
    ]

    assert len(events) == 1
    assert events[0].type == "ai_message"
