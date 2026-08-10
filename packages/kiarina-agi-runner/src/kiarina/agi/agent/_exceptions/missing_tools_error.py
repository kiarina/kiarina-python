from kiarina.agi.tool_info import ToolName


class MissingToolsError(Exception):
    def __init__(self, tool_names: list[ToolName]) -> None:
        unique_tool_names = list(dict.fromkeys(tool_names))
        self.tool_names: list[ToolName] = unique_tool_names
        super().__init__(f"Missing tools: {', '.join(unique_tool_names)}")
