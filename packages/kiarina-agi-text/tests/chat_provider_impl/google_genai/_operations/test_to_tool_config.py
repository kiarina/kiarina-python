from kiarina.agi.chat_provider_impl.google_genai._operations.to_tool_config import (
    to_tool_config,
)
from kiarina.agi.tool_info import ToolInfo


def test_to_tool_config(tool_infos: list[ToolInfo], tool_info: ToolInfo) -> None:
    assert to_tool_config(None, tool_infos) == {
        "function_calling_config": {"mode": "AUTO"}
    }
    assert to_tool_config("any", tool_infos) == {
        "function_calling_config": {"mode": "ANY"}
    }
    assert to_tool_config("any", [tool_info]) == {
        "function_calling_config": {
            "mode": "ANY",
            "allowed_function_names": ["get_weather"],
        }
    }
    assert to_tool_config("get_news", tool_infos) == {
        "function_calling_config": {
            "mode": "ANY",
            "allowed_function_names": ["get_news"],
        }
    }
