import pytest
from pydantic import BaseModel

from kiarina.agi.tool_info import ToolInfo


@pytest.fixture
def tool_info() -> ToolInfo:
    class ArgsSchema(BaseModel):
        arg1: str
        arg2: int

    return ToolInfo(
        name="my_tool",
        description="This is a test tool.",
        args_schema=ArgsSchema.model_json_schema(),
    )


def test_to_estimates(tool_info: ToolInfo) -> None:
    estimates = tool_info.to_estimates()
    assert estimates.token_count > 0


def test_to_json_schema(tool_info: ToolInfo) -> None:
    json_schema = tool_info.to_json_schema()
    assert json_schema["title"] == "my_tool"
    assert json_schema["description"] == "This is a test tool."
    assert "arg1" in json_schema["properties"]
    assert "arg2" in json_schema["properties"]

    import json

    print("JSON Schema:", json.dumps(json_schema, indent=2, ensure_ascii=False))
