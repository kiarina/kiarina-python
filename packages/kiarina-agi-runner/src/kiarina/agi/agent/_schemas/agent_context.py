from dataclasses import dataclass, field
from typing import Any, Self

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolOptions
from kiarina.agi.workflow import WorkflowOptions


@dataclass
class AgentContext:
    file_limits: ChatLimits

    chat_options: ChatOptions
    prompt_options: PromptOptions
    workflow_options: WorkflowOptions
    tool_options: ToolOptions
    cost_recorder: CostRecorder
    run_context: RunContext
    run_kwargs: dict[str, Any]

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_workflow_kwargs(self) -> dict[str, Any]:
        return {
            "chat_options": self.chat_options,
            "prompt_options": self.prompt_options,
            "workflow_options": self.workflow_options,
            "cost_recorder": self.cost_recorder,
            **self.run_kwargs,
        }

    def to_tool_kwargs(self) -> dict[str, Any]:
        return {
            "tool_options": self.tool_options,
            "cost_recorder": self.cost_recorder,
            **self.run_kwargs,
        }

    @classmethod
    def create(
        cls,
        *,
        file_limits: ChatLimits | None = None,
        chat_options: ChatOptions | None = None,
        prompt_options: PromptOptions | None = None,
        workflow_options: WorkflowOptions | None = None,
        tool_options: ToolOptions | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
        **kwargs: Any,
    ) -> Self:
        return cls(
            file_limits=file_limits or ChatLimits(),
            chat_options=chat_options or {},
            prompt_options=prompt_options or {},
            workflow_options=workflow_options or {},
            tool_options=tool_options or {},
            cost_recorder=cost_recorder or NullCostRecorder(),
            run_context=run_context,
            run_kwargs=kwargs,
        )
