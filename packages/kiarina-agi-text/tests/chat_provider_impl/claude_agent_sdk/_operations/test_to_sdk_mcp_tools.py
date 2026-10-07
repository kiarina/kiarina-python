from kiarina.agi.chat_provider_impl.claude_agent_sdk._operations.to_sdk_mcp_tools import (
    to_sdk_mcp_tools,
)
from kiarina.agi.tool_info import create_tool_info


async def test_to_sdk_mcp_tools() -> None:
    tool_info = create_tool_info(
        {
            "title": "get_weather",
            "description": "Get the weather.",
            "properties": {"city": {"type": "string"}},
        }
    )

    tools = to_sdk_mcp_tools([tool_info])

    assert [t.name for t in tools] == ["get_weather"]
    assert tools[0].description == "Get the weather."
    assert tools[0].input_schema == {
        "properties": {"city": {"type": "string"}},
        "type": "object",
    }

    result = await tools[0].handler({"city": "Nagoya"})
    assert result["content"][0]["text"].startswith("Not run here.")
