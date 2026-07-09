from typing import Protocol, runtime_checkable

from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext

from .tool_logger_name import ToolLoggerName


@runtime_checkable
class ToolLogger(Protocol):
    name: ToolLoggerName

    def log_tool_start(
        self,
        tool_call: ToolCall,
        run_context: RunContext,
    ) -> None: ...

    def log_tool_end(
        self,
        tool_message: ToolMessage,
        run_context: RunContext,
    ) -> None: ...
