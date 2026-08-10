from typing import TypeAlias

from kiarina.agi.tool_info import ToolName

ToolInfoSpecifier: TypeAlias = ToolName | str
"""
A string in one of the following formats:

- {ToolName}
- {ToolState}:{ToolName}
- {JSONString}

Examples:
- "run"
- "active:run"
- '{"name": "hello", "description": "Says hello", "args_schema": {...}, "state": "active"}'
"""
