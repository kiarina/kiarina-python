from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext

from .._types.workflow_options import WorkflowOptions
from .run_workflow import run_workflow


async def stream_workflow(
    history: History,
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    workflow_options: WorkflowOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    chat_options = chat_options or {}
    chat_options["streaming"] = True

    async for event in run_workflow(
        history,
        chat_options=chat_options,
        prompt_options=prompt_options,
        workflow_options=workflow_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    ):
        yield event
