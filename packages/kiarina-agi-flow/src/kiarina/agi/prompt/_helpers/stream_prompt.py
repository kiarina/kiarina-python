from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from .._types.prompt_options import PromptOptions
from .run_prompt import run_prompt


async def stream_prompt(
    history: History,
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    chat_options = chat_options or {}
    chat_options["streaming"] = True

    async for event in run_prompt(
        history,
        chat_options=chat_options,
        prompt_options=prompt_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    ):
        yield event
