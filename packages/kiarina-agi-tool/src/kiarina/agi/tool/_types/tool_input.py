from typing import TypeAlias

from .tool import Tool
from .tool_specifier import ToolSpecifier

ToolInput: TypeAlias = Tool | ToolSpecifier
