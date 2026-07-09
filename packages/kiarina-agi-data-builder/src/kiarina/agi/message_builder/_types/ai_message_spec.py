from typing import NotRequired

from kiarina.agi.content_builder import ContentSpec

from .tool_call_spec import ToolCallSpec


class AIMessageSpec(ContentSpec):
    tool_calls: NotRequired[list[ToolCallSpec]]
