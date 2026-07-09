from kiarina.agi.tool_info import ToolName

from .tool_error import ToolError


class ToolNotFoundError(ToolError):
    def __init__(self, tool_name: ToolName) -> None:
        self.tool_name: ToolName = tool_name
        super().__init__(f"Tool not found: {tool_name}")
