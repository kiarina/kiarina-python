from kiarina.agi.chat_provider_impl.anthropic._operations.to_anthropic_tools import (
    to_anthropic_tools,
)
from kiarina.agi.tool_info import ToolInfo


def test_to_anthropic_tools() -> None:
    tool_infos = [
        ToolInfo(
            name="write_file",
            description="Write a file.",
            args_schema={
                "title": "WriteFile",
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
            cache_control={"type": "ephemeral"},
        ),
        ToolInfo(name="noop", description="No operation."),
    ]

    assert to_anthropic_tools(tool_infos, cache_ttl="5m") == [
        {
            "name": "write_file",
            "description": "Write a file.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
            "cache_control": {"type": "ephemeral"},
        },
        {
            "name": "noop",
            "description": "No operation.",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]


def test_cache_ttl_1h() -> None:
    tool_info = ToolInfo(
        name="noop", description="No operation.", cache_control={"type": "ephemeral"}
    )

    assert to_anthropic_tools([tool_info], cache_ttl="1h")[0]["cache_control"] == {
        "type": "ephemeral",
        "ttl": "1h",
    }
