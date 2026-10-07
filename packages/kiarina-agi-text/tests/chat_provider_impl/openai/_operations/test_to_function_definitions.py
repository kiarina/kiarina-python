from kiarina.agi.chat_provider_impl.openai._operations.to_function_definitions import (
    to_function_definitions,
)
from kiarina.agi.tool_info import ToolInfo


def test_to_function_definitions() -> None:
    tool_info = ToolInfo(
        name="write_file",
        description="Write a file.",
        args_schema={
            "title": "WriteFile",
            "description": "Ignored",
            "type": "object",
            "properties": {
                "title": {"title": "Title", "type": "string"},
                "tags": {
                    "title": "Tags",
                    "type": "array",
                    "items": {"title": "Tag", "type": "string"},
                },
            },
            "anyOf": [{"title": "A", "required": ["title"]}],
        },
    )

    assert to_function_definitions([tool_info]) == [
        {
            "name": "write_file",
            "description": "Write a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "anyOf": [{"required": ["title"]}],
            },
        }
    ]


def test_to_function_definitions_without_args() -> None:
    tool_info = ToolInfo(name="noop", description="No operation.")

    assert to_function_definitions([tool_info])[0]["parameters"] == {
        "type": "object",
        "properties": {},
    }
