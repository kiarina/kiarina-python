from typing import Any

from kiarina.agi.tool_info import ToolInfo

_NOT_RUN = "Not run here. The caller runs this tool and sends the result."


def to_sdk_mcp_tools(tool_infos: list[ToolInfo]) -> list[Any]:
    """
    Tools for an SDK MCP server. Their handlers never do the work: the request
    stops after the model turn (`max_turns=1`), and the caller runs the tools.
    Claude Code still calls the handlers before it stops.
    """
    from claude_agent_sdk import tool

    tools: list[Any] = []

    for tool_info in tool_infos:
        input_schema = {
            k: v
            for k, v in tool_info.args_schema.items()
            if k not in ("title", "description")
        }
        input_schema.setdefault("type", "object")
        input_schema.setdefault("properties", {})

        @tool(tool_info.name, tool_info.description, input_schema)
        async def _handler(args: dict[str, Any]) -> dict[str, Any]:
            return {"content": [{"type": "text", "text": _NOT_RUN}]}

        tools.append(_handler)

    return tools
