from kiarina.agi.data.message import ToolCall


def test_to_estimates() -> None:
    tool_call = ToolCall(
        id="123",
        name="test_tool",
        args={
            "arg1": "value1",
            "arg2": 42,
        },
    )

    estimates = tool_call.to_estimates()

    print(estimates)


def test_to_text() -> None:
    tool_call = ToolCall(
        id="123",
        name="test_tool",
        args={
            "arg1": "value1",
            "arg2": 42,
        },
    )

    text = tool_call.to_text()

    print(text)
