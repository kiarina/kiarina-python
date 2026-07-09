from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_logger_impl.null import NullToolLogger


def test_null_tool_logger(run_context: RunContext) -> None:
    tool_logger = NullToolLogger()
    tool_call = ToolCall(id="1", name="my_tool")
    tool_message = ToolMessage.create(
        tool_name="my_tool",
        tool_call_id="1",
    )

    tool_logger.log_tool_start(tool_call, run_context)
    tool_logger.log_tool_end(tool_message, run_context)
