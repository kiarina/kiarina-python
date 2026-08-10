from typing import TypeAlias

from kiarina.agi.tool_info import ToolInfo

from .tool_info_specifier import ToolInfoSpecifier

ToolInfoInput: TypeAlias = ToolInfo | ToolInfoSpecifier
