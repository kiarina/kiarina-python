from typing import Any

from kiarina.agi.tool_info import ToolInfo

from .._types.cache_ttl import CacheTTL


def to_anthropic_tools(
    tool_infos: list[ToolInfo], *, cache_ttl: CacheTTL
) -> list[dict[str, Any]]:
    """A tool's `cache_control` gets the configured TTL when it is `1h`."""
    tools: list[dict[str, Any]] = []

    for tool_info in tool_infos:
        input_schema = {
            k: v
            for k, v in tool_info.args_schema.items()
            if k not in ("title", "description")
        }
        input_schema.setdefault("type", "object")
        input_schema.setdefault("properties", {})

        tool: dict[str, Any] = {
            "name": tool_info.name,
            "description": tool_info.description,
            "input_schema": input_schema,
        }

        if tool_info.cache_control:
            tool["cache_control"] = (
                {"type": "ephemeral", "ttl": "1h"}
                if cache_ttl == "1h"
                else tool_info.cache_control
            )

        tools.append(tool)

    return tools
