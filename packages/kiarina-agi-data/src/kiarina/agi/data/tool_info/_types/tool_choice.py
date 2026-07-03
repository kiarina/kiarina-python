from typing import Literal

from .tool_name import ToolName

ToolChoice = (
    Literal[
        "auto",
        "any",
    ]
    | ToolName
)
"""
Tool selection method

- `auto`: LLM decides whether to use tools
- `any`: Tools must be used
- `<tool_name>`: Specific tool to use
"""
