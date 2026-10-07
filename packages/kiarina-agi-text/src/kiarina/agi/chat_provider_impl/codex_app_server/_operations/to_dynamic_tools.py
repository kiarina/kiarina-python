from typing import Any

from kiarina.agi.tool_info import ToolInfo


def to_dynamic_tools(tool_infos: list[ToolInfo]) -> list[dict[str, Any]]:
    """`dynamicTools` for `thread/start`. Codex asks the client to run them."""
    tools: list[dict[str, Any]] = []

    for tool_info in tool_infos:
        input_schema = {
            k: v
            for k, v in tool_info.args_schema.items()
            if k not in ("title", "description")
        }
        input_schema.setdefault("type", "object")
        input_schema.setdefault("properties", {})

        tools.append(
            {
                "type": "function",
                "name": tool_info.name,
                "description": tool_info.description,
                "inputSchema": input_schema,
            }
        )

    return tools
