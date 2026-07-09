from typing import TypeAlias

from kiarina.agi.tool_info import ToolName

ToolSpecifier: TypeAlias = ToolName | str
"""
A string in the form of "{ToolName}?{ConfigString}"

Examples:
- "run"
- "run?key1=value1&key2=value2"
"""
