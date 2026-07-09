import asyncio
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.agent import AgentOptions, run_agent
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.history_builder import HistoryInput, resolve_history
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolOptions, tool_registry
from kiarina.agi.workflow import WorkflowOptions


async def run_task(
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
    prompt_options = prompt_options or {}
    workflow_options = workflow_options or {}
    agent_options = agent_options or {}

    if not prompt_options.get("prompt"):
        prompt_options["prompt"] = "vanilla"

    if not workflow_options.get("workflow"):
        workflow_options["workflow"] = "vanilla"

    if not agent_options.get("agent"):
        agent_options["agent"] = "vanilla"

    history = await resolve_history(history_input, run_context=run_context)

    _add_tool_infos_from_tool_options(history, tool_options)

    async for event in run_agent(
        history,
        chat_options=chat_options,
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


def _add_tool_infos_from_tool_options(
    history: History, tool_options: ToolOptions | None
) -> None:
    if not tool_options:
        return

    if tool_inputs := tool_options.get("tools"):
        for tool_input in tool_inputs:
            tool = tool_registry.resolve(tool_input)

            if not history.get_tool_info(name=tool.name):
                history.add_tool_info(tool.to_tool_info())
