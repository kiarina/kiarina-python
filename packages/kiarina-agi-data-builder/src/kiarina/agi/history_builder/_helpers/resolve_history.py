from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from .._types.history_input import HistoryInput
from .._types.history_spec import HistorySpec
from .build_history import build_history


async def resolve_history(
    history_input: HistoryInput,
    *,
    run_context: RunContext,
) -> History:
    if isinstance(history_input, History):
        return history_input

    if isinstance(history_input, dict):
        spec = history_input
    elif isinstance(history_input, list):
        spec = HistorySpec(events=history_input)
    elif isinstance(history_input, str):
        spec = HistorySpec(events=history_input)
    else:  # pragma: no cover
        raise TypeError(f"Unsupported history input type: {type(history_input)}")

    return await build_history(spec, run_context=run_context)
