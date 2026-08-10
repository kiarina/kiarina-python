from kiarina.agi.agent import invoke_agent
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext


async def test_invoke_agent(history: History, run_context: RunContext) -> None:
    events = [e async for e in invoke_agent(history, run_context=run_context)]
    assert len(events) == 1
    assert events[0].type == "ai_message"
