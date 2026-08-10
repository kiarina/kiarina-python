from kiarina.agi.event_builder import build_events
from kiarina.agi.file_info_loader import load_file_infos
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info_builder import resolve_tool_info

from .._types.history_spec import HistorySpec


async def build_history(
    spec: HistorySpec,
    *,
    run_context: RunContext,
) -> History:
    history = History()

    if tool_info_inputs := spec.get("tool_infos"):
        history.tool_infos = [
            resolve_tool_info(tool_info_input, language=run_context.language)
            for tool_info_input in tool_info_inputs
        ]

    if file_info_inputs := spec.get("file_infos"):
        history.file_infos = await load_file_infos(
            file_info_inputs, run_context=run_context
        )

    if events_input := spec.get("events"):
        for event in await build_events(events_input, run_context=run_context):
            history.add_event(event)

    return history
