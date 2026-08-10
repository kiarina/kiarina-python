from dataclasses import dataclass, field
from typing import Any, Self

from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext


@dataclass
class StateContext:
    history: History
    chat_options: ChatOptions
    prompt_options: PromptOptions
    cost_recorder: CostRecorder
    run_context: RunContext
    run_kwargs: dict[str, Any]

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "history": self.history,
            "chat_options": self.chat_options,
            "prompt_options": self.prompt_options,
            "cost_recorder": self.cost_recorder,
            "run_context": self.run_context,
            "run_kwargs": self.run_kwargs,
            "metadata": self.metadata,
        }

    @classmethod
    def create(
        cls,
        *,
        history: History | None = None,
        chat_options: ChatOptions | None = None,
        prompt_options: PromptOptions | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
        **kwargs: Any,
    ) -> Self:
        return cls(
            history=history or History(),
            chat_options=chat_options or ChatOptions(),
            prompt_options=prompt_options or PromptOptions(),
            cost_recorder=cost_recorder or NullCostRecorder(),
            run_context=run_context,
            run_kwargs=kwargs,
        )
