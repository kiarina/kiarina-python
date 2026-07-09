import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.state import StateContext
from kiarina.agi.state_machine import StateMachine

from .._models.base_workflow import BaseWorkflow


def workflow(
    func: Callable[..., StateMachine | Awaitable[StateMachine]],
) -> type[BaseWorkflow]:
    class WorkflowClass(BaseWorkflow):
        async def get_state_machine(
            self,
            *,
            history: History,
            chat_options: ChatOptions,
            prompt_options: PromptOptions,
            cost_recorder: CostRecorder,
            run_context: RunContext,
            **kwargs: Any,
        ) -> StateMachine:
            ctx = StateContext.create(
                history=history,
                chat_options=chat_options,
                prompt_options=prompt_options,
                cost_recorder=cost_recorder,
                run_context=run_context,
                **kwargs,
            )

            sm = func(
                ctx,
                **self.init_kwargs,
            )

            if inspect.iscoroutine(sm):
                return await cast(Awaitable[StateMachine], sm)

            return cast(StateMachine, sm)

    WorkflowClass.__name__ = func.__name__
    WorkflowClass.__qualname__ = func.__qualname__
    WorkflowClass.__module__ = func.__module__
    WorkflowClass.__doc__ = func.__doc__

    return WorkflowClass
