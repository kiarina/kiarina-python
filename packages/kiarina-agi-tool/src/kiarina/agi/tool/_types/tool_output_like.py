from collections.abc import AsyncIterator, Awaitable
from typing import TypeAlias

from .tool_output import ToolOutput

ToolOutputLike: TypeAlias = (
    ToolOutput | Awaitable[ToolOutput] | AsyncIterator[ToolOutput]
)
