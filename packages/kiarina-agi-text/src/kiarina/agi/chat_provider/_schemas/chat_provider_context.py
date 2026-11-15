from dataclasses import dataclass
from typing import Self

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice, ToolInfo

from .chat_capabilities import ChatCapabilities


@dataclass
class ChatProviderContext:
    messages: list[Message]
    tool_infos: list[ToolInfo] | None
    tool_choice: ToolChoice | None
    parallel_tool_calls: bool | None
    streaming: bool | None
    capabilities: ChatCapabilities
    cost_recorder: CostRecorder
    run_context: RunContext
    cost_record: CostRecord | None = None

    @classmethod
    def create(
        cls,
        *,
        messages: list[Message] | None = None,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        capabilities: ChatCapabilities | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Self:
        return cls(
            messages=messages or [],
            tool_infos=tool_infos,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            streaming=streaming,
            capabilities=capabilities or ChatCapabilities(),
            cost_recorder=cost_recorder or NullCostRecorder(),
            run_context=run_context,
        )

    def add_cost_record(self, cost_record: CostRecord) -> None:
        if self.cost_record is not None:
            raise RuntimeError("A chat provider call records one cost")

        self.cost_record = cost_record
        self.cost_recorder.add(cost_record)
