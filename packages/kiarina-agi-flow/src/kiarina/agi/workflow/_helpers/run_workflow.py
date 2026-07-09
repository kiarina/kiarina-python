from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext

from .._services.workflow_registry import workflow_registry
from .._types.workflow import Workflow
from .._types.workflow_options import WorkflowOptions


async def run_workflow(
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
    prompt_options = prompt_options or {}
    workflow_options = workflow_options or {}
    cost_recorder = cost_recorder or NullCostRecorder()

    workflow = workflow_options.get("workflow")

    if not isinstance(workflow, Workflow):
        workflow = workflow_registry.resolve(workflow)

    run_context = run_context.with_metadata(workflow=f"{workflow}")

    state_machine = await workflow.get_state_machine(
        history=history,
        chat_options=chat_options,
        prompt_options=prompt_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    )

    async for event in state_machine.run():
        yield event
