from typing import Literal

from kiarina.agi.tool_info import ToolChoice, ToolName


def to_openai_tool_choice(
    tool_choice: ToolChoice | None,
) -> Literal["auto", "required"] | ToolName:
    """Map `any` to OpenAI's `required`. Any other name selects that function."""
    if tool_choice is None or tool_choice == "auto":
        return "auto"

    if tool_choice == "any":
        return "required"

    return tool_choice
