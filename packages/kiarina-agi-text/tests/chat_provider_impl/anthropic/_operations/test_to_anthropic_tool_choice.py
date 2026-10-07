import pytest

from kiarina.agi.chat_provider_impl.anthropic._operations.to_anthropic_tool_choice import (
    to_anthropic_tool_choice,
)


@pytest.mark.parametrize(
    ("tool_choice", "parallel_tool_calls", "expected"),
    [
        (None, None, {"type": "auto"}),
        ("auto", True, {"type": "auto", "disable_parallel_tool_use": False}),
        ("any", False, {"type": "any", "disable_parallel_tool_use": True}),
        ("get_weather", None, {"type": "tool", "name": "get_weather"}),
    ],
)
def test_to_anthropic_tool_choice(
    tool_choice: str | None,
    parallel_tool_calls: bool | None,
    expected: dict[str, object],
) -> None:
    assert (
        to_anthropic_tool_choice(tool_choice, parallel_tool_calls=parallel_tool_calls)
        == expected
    )


@pytest.mark.parametrize("tool_choice", ["any", "get_weather"])
def test_forced_tool_choice_unsupported(tool_choice: str) -> None:
    assert to_anthropic_tool_choice(
        tool_choice, parallel_tool_calls=False, forced_tool_choice_supported=False
    ) == {"type": "auto", "disable_parallel_tool_use": True}
