from kiarina.agi.chat_provider_impl.google_genai._operations.to_function_declarations import (
    to_function_declarations,
)
from kiarina.agi.tool_info import ToolInfo


def test_to_function_declarations() -> None:
    tool_infos = [
        ToolInfo(
            name="write_file",
            description="Write a file.",
            args_schema={
                "title": "WriteFile",
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        ),
        ToolInfo(name="noop", description="No operation."),
    ]

    assert to_function_declarations(tool_infos) == [
        {
            "name": "write_file",
            "description": "Write a file.",
            "parameters_json_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        },
        {
            "name": "noop",
            "description": "No operation.",
            "parameters_json_schema": {"type": "object", "properties": {}},
        },
    ]
