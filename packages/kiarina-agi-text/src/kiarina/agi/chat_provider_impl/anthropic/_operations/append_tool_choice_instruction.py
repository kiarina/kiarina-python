from typing import Any

from kiarina.agi.tool_info import ToolChoice


def append_tool_choice_instruction(
    messages: list[dict[str, Any]], tool_choice: ToolChoice | None
) -> None:
    """
    Ask for a tool call in the last user turn, for models that reject forced tool
    choice. Callers such as structured output rely on `any` returning a tool call.
    """
    if tool_choice is None or tool_choice == "auto":
        return

    if tool_choice == "any":
        text = "You must respond by calling one of the provided tools."
    else:
        text = f"You must respond by calling the `{tool_choice}` tool."

    for message in reversed(messages):
        if message["role"] == "user":
            message["content"] = [*message["content"], {"type": "text", "text": text}]
            return
