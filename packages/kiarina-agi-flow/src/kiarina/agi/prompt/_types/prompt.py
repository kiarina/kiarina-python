from typing import Any, Protocol, runtime_checkable

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.section_container import SectionContainer

from .prompt_name import PromptName


@runtime_checkable
class Prompt(Protocol):
    name: PromptName

    async def get_section_container(
        self,
        *,
        history: History,
        chat_options: ChatOptions,
        cost_recorder: CostRecorder,
        run_context: RunContext,
        **kwargs: Any,
    ) -> SectionContainer: ...
