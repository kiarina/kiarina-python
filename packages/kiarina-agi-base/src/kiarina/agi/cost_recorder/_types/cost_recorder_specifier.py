from typing import TypeAlias

from .cost_recorder_name import CostRecorderName

CostRecorderSpecifier: TypeAlias = CostRecorderName | str
"""
A string in the form of "{CostRecorderName}?{ConfigString}"

Examples:
- "local"
- "local?key1=value1&key2=value2"
"""
