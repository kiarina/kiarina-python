from typing import TypeAlias

from .cost_logger_name import CostLoggerName

CostLoggerSpecifier: TypeAlias = CostLoggerName | str
"""
A string in the form of "{CostLoggerName}?{ConfigString}"

Examples:
- "null"
- "null?key1=value1&key2=value2"
"""
