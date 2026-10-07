from typing import Any

from kiarina.agi.tool_info import ToolChoice, ToolInfo


def to_tool_config(
    tool_choice: ToolChoice | None, tool_infos: list[ToolInfo]
) -> dict[str, Any]:
    """`any` with a single tool names that tool, as `lc_google` did."""
    if tool_choice is None or tool_choice == "auto":
        return {"function_calling_config": {"mode": "AUTO"}}

    if tool_choice == "any":
        config: dict[str, Any] = {"mode": "ANY"}

        if len(tool_infos) == 1:
            config["allowed_function_names"] = [tool_infos[0].name]

        return {"function_calling_config": config}

    return {
        "function_calling_config": {
            "mode": "ANY",
            "allowed_function_names": [tool_choice],
        }
    }
