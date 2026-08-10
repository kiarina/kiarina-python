from typing import Any

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history_builder import HistoryInput, resolve_history
from kiarina.agi.prompt import PromptOptions, invoke_prompt
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import create_tool_info


async def generate_dict(
    history_input: HistoryInput,
    json_schema: dict[str, Any],
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> dict[str, Any]:
    chat_options = chat_options or {}
    chat_options["tool_choice"] = "any"

    prompt_options = prompt_options or {}

    if not prompt_options.get("prompt"):
        prompt_options["prompt"] = "vanilla"

    history = await resolve_history(history_input, run_context=run_context)
    history.tool_infos = [create_tool_info(json_schema)]

    events = [
        event
        async for event in invoke_prompt(
            history,
            chat_options=chat_options,
            prompt_options=prompt_options,
            cost_recorder=cost_recorder,
            run_context=run_context,
            **kwargs,
        )
    ]

    ai_message_events = [event for event in events if event.type == "ai_message"]

    if not ai_message_events:  # pragma: no cover
        raise RuntimeError("AI message was not generated")

    tool_calls = ai_message_events[-1].message.tool_calls

    if not tool_calls:  # pragma: no cover
        raise RuntimeError("No tool call was generated")

    return tool_calls[0].args
