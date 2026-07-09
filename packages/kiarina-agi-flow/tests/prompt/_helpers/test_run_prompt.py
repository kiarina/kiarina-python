from kiarina.agi.history import History
from kiarina.agi.prompt import run_prompt
from kiarina.agi.run_context import RunContext


async def test_run_prompt(history: History, run_context: RunContext) -> None:
    events = [e async for e in run_prompt(history, run_context=run_context)]
    assert len(events) == 1
    assert events[0].type == "ai_message"


async def test_chat_limits_specifier(history: History, run_context: RunContext) -> None:
    events = [
        e
        async for e in run_prompt(
            history,
            prompt_options={"limits": "token_count_limit=1000"},
            run_context=run_context,
        )
    ]
    assert len(events) == 1
    assert events[0].type == "ai_message"
