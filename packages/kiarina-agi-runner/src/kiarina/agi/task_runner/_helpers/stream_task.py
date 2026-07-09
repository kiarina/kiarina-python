import asyncio
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.agent import AgentOptions
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history_builder import HistoryInput
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolOptions
from kiarina.agi.workflow import WorkflowOptions

from .run_task import run_task


async def stream_task(
    history_input: HistoryInput,
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    workflow_options: WorkflowOptions | None = None,
    tool_options: ToolOptions | None = None,
    agent_options: AgentOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    stop_event: asyncio.Event | None = None,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    async for event in run_task(
        history_input,
        chat_options={**(chat_options or {}), "streaming": True},
        prompt_options=prompt_options,
        workflow_options=workflow_options,
        tool_options=tool_options,
        agent_options=agent_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
        stop_event=stop_event,
        **kwargs,
    ):
        yield event
