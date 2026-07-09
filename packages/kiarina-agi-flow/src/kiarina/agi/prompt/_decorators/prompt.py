import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext
from kiarina.agi.section_container import SectionContainer

from .._models.base_prompt import BasePrompt


def prompt(
    func: Callable[..., SectionContainer | Awaitable[SectionContainer]],
) -> type[BasePrompt]:
    class PromptClass(BasePrompt):
        async def get_section_container(
            self,
            *,
            history: History,
            chat_options: ChatOptions,
            cost_recorder: CostRecorder,
            run_context: RunContext,
            **kwargs: Any,
        ) -> SectionContainer:
            ctx = SectionContext.create(
                history=history,
                chat_options=chat_options,
                cost_recorder=cost_recorder,
                run_context=run_context,
                **kwargs,
            )

            sc = func(
                ctx,
                **self.init_kwargs,
            )

            if inspect.iscoroutine(sc):
                return await cast(Awaitable[SectionContainer], sc)

            return cast(SectionContainer, sc)

    PromptClass.__name__ = func.__name__
    PromptClass.__qualname__ = func.__qualname__
    PromptClass.__module__ = func.__module__
    PromptClass.__doc__ = func.__doc__

    return PromptClass
