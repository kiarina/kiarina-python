from typing import Any

from kiarina.agi.tool_info import ToolChoice


def to_anthropic_tool_choice(
    tool_choice: ToolChoice | None, *, parallel_tool_calls: bool | None
) -> dict[str, Any]:
    if tool_choice is None or tool_choice == "auto":
        result: dict[str, Any] = {"type": "auto"}
    elif tool_choice == "any":
        result = {"type": "any"}
    else:
        result = {"type": "tool", "name": tool_choice}

    if parallel_tool_calls is not None:
        result["disable_parallel_tool_use"] = not parallel_tool_calls

    return result
