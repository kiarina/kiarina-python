from abc import ABC, abstractmethod
from typing import Any

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.state_machine import StateMachine

from .._types.workflow import Workflow
from .._types.workflow_name import WorkflowName


class BaseWorkflow(Workflow, ABC):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: WorkflowName | None = None

    def __str__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> WorkflowName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Workflow name not set")

        return self._name

    @name.setter
    def name(self, value: WorkflowName) -> None:
        self._name = value

    @abstractmethod
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
