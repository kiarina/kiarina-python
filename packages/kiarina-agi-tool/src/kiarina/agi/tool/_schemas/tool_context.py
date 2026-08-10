from dataclasses import dataclass, field
from typing import Any, Self

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext


@dataclass
class ToolContext:
    tool_call: ToolCall
    history: History
    cost_recorder: CostRecorder
    run_context: RunContext
    run_kwargs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        tool_call: ToolCall,
        history: History | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
        **kwargs: Any,
    ) -> Self:
        return cls(
            tool_call=tool_call,
            history=history or History(),
            cost_recorder=cost_recorder or NullCostRecorder(),
            run_context=run_context,
            run_kwargs=kwargs,
        )
