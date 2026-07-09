from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from kiarina.agi.event import Event
from kiarina.agi.tool_info import ToolInfo, ToolName
from kiarina.i18n import Language

from .._schemas.tool_context import ToolContext


@runtime_checkable
class Tool(Protocol):
    name: ToolName
    tool_schema: type[BaseModel]
    return_direct: bool
    accepts_ctx: bool

    def to_tool_info(self, language: Language | None = None) -> ToolInfo: ...

    def run(self, ctx: ToolContext) -> AsyncIterator[Event]: ...
