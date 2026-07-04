import json

from pydantic import BaseModel

from kiarina.agi.langchain_chat_provider import from_tool_infos
from kiarina.agi.tool_info import ToolInfo, create_tool_info


def test_from_tool_infos() -> None:

    class ArgsSchema(BaseModel):
        arg1: str
        arg2: int

    tool_infos = [
        create_tool_info(ArgsSchema, name="tool1", description="This is tool 1."),
        create_tool_info(ArgsSchema, name="tool2", description="This is tool 2."),
    ]

    lc_tool_infos = from_tool_infos(tool_infos)
    assert len(lc_tool_infos) == 2
    assert lc_tool_infos[0]["name"] == "tool1"
    assert lc_tool_infos[0]["description"] == "This is tool 1."
    assert lc_tool_infos[0]["parameters"]["properties"]["arg1"]["type"] == "string"
    assert lc_tool_infos[0]["parameters"]["properties"]["arg2"]["type"] == "integer"
    assert lc_tool_infos[1]["name"] == "tool2"
    assert lc_tool_infos[1]["description"] == "This is tool 2."
    assert lc_tool_infos[1]["parameters"]["properties"]["arg1"]["type"] == "string"
    assert lc_tool_infos[1]["parameters"]["properties"]["arg2"]["type"] == "integer"

    for lc_tool_info in lc_tool_infos:
        print("LC Tool Info:", json.dumps(lc_tool_info, indent=2, ensure_ascii=False))


def test_no_args() -> None:
    tool_info = ToolInfo(name="no_args_tool", description="This tool has no arguments.")
    lc_tool_infos = from_tool_infos([tool_info])
    print(json.dumps(lc_tool_infos[0], indent=2, ensure_ascii=False))
