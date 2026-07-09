from kiarina.agi.history import History
from kiarina.agi.prompt import invoke_prompt
from kiarina.agi.run_context import RunContext


async def test_invoke_prompt(history: History, run_context: RunContext) -> None:
    events = [e async for e in invoke_prompt(history, run_context=run_context)]
    assert len(events) == 1
    assert events[0].type == "ai_message"
