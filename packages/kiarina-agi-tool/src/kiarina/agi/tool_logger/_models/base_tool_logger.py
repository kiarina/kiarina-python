from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext

from .._types.tool_logger import ToolLogger
from .._types.tool_logger_name import ToolLoggerName


class BaseToolLogger(ToolLogger):
    def __init__(self) -> None:
        self._name: ToolLoggerName | None = None

    @property
    def name(self) -> ToolLoggerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Tool logger name not set")

        return self._name

    @name.setter
    def name(self, value: ToolLoggerName) -> None:
        self._name = value

    def log_tool_start(
        self,
        tool_call: ToolCall,
        run_context: RunContext,
    ) -> None:
        pass

    def log_tool_end(
        self,
        tool_message: ToolMessage,
        run_context: RunContext,
    ) -> None:
        pass
