from typing import Any, NotRequired, TypedDict


class ToolCallSpec(TypedDict):
    id: NotRequired[str]
    name: str
    args: NotRequired[dict[str, Any]]
