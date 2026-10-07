import pytest
from claude_agent_sdk import ResultMessage, TextBlock, ThinkingBlock, ToolUseBlock

from kiarina.agi.chat_provider_impl.claude_code._operations.from_claude_agent_sdk_messages import (
    from_claude_agent_sdk_messages,
)


def _result_message() -> ResultMessage:
    return ResultMessage(
        subtype="error_max_turns",
        duration_ms=1,
        duration_api_ms=1,
        is_error=True,
        num_turns=1,
        session_id="s",
        stop_reason="tool_use",
        total_cost_usd=0.01,
        usage={"input_tokens": 10, "output_tokens": 5},
    )


@pytest.mark.parametrize(
    ("parallel_tool_calls", "tool_names"),
    [(True, ["get_weather", "get_time"]), (False, ["get_weather"])],
)
def test_from_claude_agent_sdk_messages(
    parallel_tool_calls: bool, tool_names: list[str]
) -> None:
    result = from_claude_agent_sdk_messages(
        [
            ThinkingBlock(thinking="...", signature="sig"),
            TextBlock(text="Checking."),
            ToolUseBlock(
                id="toolu_1", name="mcp__app__get_weather", input={"city": "Nagoya"}
            ),
            ToolUseBlock(id="toolu_2", name="mcp__app__get_time", input={}),
        ],
        _result_message(),
        parallel_tool_calls=parallel_tool_calls,
    )

    assert result.ai_message.to_text().startswith("Checking.")
    assert [tc.name for tc in result.ai_message.tool_calls] == tool_names
    assert result.ai_message.tool_calls[0].id == "toolu_1"
    assert result.ai_message.tool_calls[0].args == {"city": "Nagoya"}
    assert result.stop_reason == "tool_use"
    assert result.usage == {"input_tokens": 10, "output_tokens": 5}
    assert result.total_cost_usd == 0.01
