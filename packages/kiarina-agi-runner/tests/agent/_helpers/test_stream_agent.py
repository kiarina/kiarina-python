from kiarina.agi.agent import stream_agent
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext


async def test_stream_agent(history: History, run_context: RunContext) -> None:
    events = [e async for e in stream_agent(history, run_context=run_context)]
    assert len(events) >= 1
