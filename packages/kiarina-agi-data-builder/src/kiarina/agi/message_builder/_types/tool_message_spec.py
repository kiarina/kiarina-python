from typing import Any, NotRequired

from kiarina.agi.content_builder import ContentSpec
from kiarina.agi.display_content import DisplayContent


class ToolMessageSpec(ContentSpec):
    tool_name: str
    tool_call_args: NotRequired[dict[str, Any]]
    tool_call_id: str
    return_direct: NotRequired[bool]
    failed: NotRequired[bool]
    artifact: NotRequired[dict[str, Any]]
    metadata: NotRequired[dict[str, Any]]
    display_contents: NotRequired[list[DisplayContent]]
