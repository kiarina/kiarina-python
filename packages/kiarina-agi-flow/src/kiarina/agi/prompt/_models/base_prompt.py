from abc import ABC, abstractmethod
from typing import Any

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.section_container import SectionContainer

from .._types.prompt import Prompt
from .._types.prompt_name import PromptName


class BasePrompt(Prompt, ABC):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: PromptName | None = None

    def __str__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> PromptName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Prompt name not set")

        return self._name

    @name.setter
    def name(self, value: PromptName) -> None:
        self._name = value

    @abstractmethod
    async def get_section_container(
        self,
        *,
        history: History,
        chat_options: ChatOptions,
        cost_recorder: CostRecorder,
        run_context: RunContext,
        **kwargs: Any,
    ) -> SectionContainer: ...
