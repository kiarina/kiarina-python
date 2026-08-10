from typing import Any, Protocol, runtime_checkable

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.state_machine import StateMachine

from .workflow_name import WorkflowName


@runtime_checkable
class Workflow(Protocol):
    name: WorkflowName

    async def get_state_machine(
        self,
        *,
        history: History,
        chat_options: ChatOptions,
        prompt_options: PromptOptions,
        cost_recorder: CostRecorder,
        run_context: RunContext,
        **kwargs: Any,
    ) -> StateMachine: ...
