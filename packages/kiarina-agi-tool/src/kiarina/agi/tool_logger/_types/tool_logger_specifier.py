from typing import TypeAlias

from .tool_logger_name import ToolLoggerName

ToolLoggerSpecifier: TypeAlias = ToolLoggerName | str
"""
A string in the form of "{ToolLoggerName}?{ConfigString}"

Examples:
- "null"
- "null?key1=value1&key2=value2"
"""
