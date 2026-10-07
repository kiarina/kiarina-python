from kiarina.agi.chat_provider_impl.codex_app_server._operations.to_dynamic_tools import (
    to_dynamic_tools,
)
from kiarina.agi.tool_info import create_tool_info


def test_to_dynamic_tools() -> None:
    tool_info = create_tool_info(
        {"title": "noop", "description": "Do nothing.", "properties": {}}
    )

    assert to_dynamic_tools([tool_info]) == [
        {
            "type": "function",
            "name": "noop",
            "description": "Do nothing.",
            "inputSchema": {"properties": {}, "type": "object"},
        }
    ]
