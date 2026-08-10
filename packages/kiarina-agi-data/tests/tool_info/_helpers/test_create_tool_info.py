from pydantic import BaseModel

from kiarina.agi.tool_info import create_tool_info


class MyTool(BaseModel):
    """This is a test tool."""

    arg1: str
    arg2: int


def test_base_model() -> None:
    tool_info = create_tool_info(MyTool)

    assert tool_info.name == "MyTool"
    assert tool_info.description == "This is a test tool."
    assert tool_info.args_schema["properties"]["arg1"]["type"] == "string"
    assert tool_info.args_schema["properties"]["arg2"]["type"] == "integer"

    print(tool_info)


def test_dict() -> None:
    tool_info = create_tool_info(MyTool.model_json_schema())

    assert tool_info.name == "MyTool"
    assert tool_info.description == "This is a test tool."
    assert tool_info.args_schema["properties"]["arg1"]["type"] == "string"
    assert tool_info.args_schema["properties"]["arg2"]["type"] == "integer"

    print(tool_info)


def test_override_name_description() -> None:
    tool_info = create_tool_info(
        MyTool,
        name="OverriddenName",
        description="Overridden description.",
    )

    assert tool_info.name == "OverriddenName"
    assert tool_info.description == "Overridden description."
    assert tool_info.args_schema["properties"]["arg1"]["type"] == "string"
    assert tool_info.args_schema["properties"]["arg2"]["type"] == "integer"

    print(tool_info)
