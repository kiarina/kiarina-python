from dataclasses import dataclass, replace
from typing import Any, Self

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice

from .._types.lc_message import LCMessage
from .._types.lc_tool_info import LCToolInfo


@dataclass
class LangChainChatProviderContext:
    lc_messages: list[LCMessage]
    lc_tool_infos: list[LCToolInfo] | None
    tool_choice: ToolChoice | None
    parallel_tool_calls: bool | None
    cost_recorder: CostRecorder
    run_context: RunContext

    def model_copy(self, **changes: Any) -> Self:
        return replace(self, **changes)

    @classmethod
    def create(
        cls,
        *,
        lc_messages: list[LCMessage] | None = None,
        lc_tool_infos: list[LCToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Self:
        return cls(
            lc_messages=lc_messages or [],
            lc_tool_infos=lc_tool_infos,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            cost_recorder=cost_recorder or NullCostRecorder(),
            run_context=run_context,
        )
