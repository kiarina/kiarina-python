from kiarina.agi.history import History
from kiarina.agi.history_builder import resolve_history
from kiarina.agi.run_context import RunContext


async def test_resolve_history(run_context: RunContext) -> None:
    kwargs = {"run_context": run_context}

    history = await resolve_history(History(), **kwargs)
    assert history.events == []

    history = await resolve_history({"events": ["Hello"]}, **kwargs)
    assert len(history.events) == 1

    history = await resolve_history(["Hello"], **kwargs)
    assert len(history.events) == 1

    history = await resolve_history("Hello", **kwargs)
    assert len(history.events) == 1
