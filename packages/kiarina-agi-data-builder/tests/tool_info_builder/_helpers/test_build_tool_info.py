from kiarina.agi.tool_info_builder import build_tool_info


def test_build_tool_info() -> None:
    tool_info = build_tool_info("hello", language="en")
    assert tool_info.name == "hello"

    tool_info = build_tool_info("disabled:hello", language="en")
    assert tool_info.name == "hello"
    assert tool_info.state == "disabled"

    tool_info.state = "inactive"
    tool_info = build_tool_info(tool_info.model_dump_json(), language="en")
    assert tool_info.name == "hello"
    assert tool_info.state == "inactive"
