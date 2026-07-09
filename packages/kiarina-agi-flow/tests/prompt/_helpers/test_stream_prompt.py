from kiarina.agi.history import History
from kiarina.agi.prompt import stream_prompt
from kiarina.agi.run_context import RunContext


async def test_stream_prompt(history: History, run_context: RunContext) -> None:
    events = [e async for e in stream_prompt(history, run_context=run_context)]
    assert len(events) >= 1
