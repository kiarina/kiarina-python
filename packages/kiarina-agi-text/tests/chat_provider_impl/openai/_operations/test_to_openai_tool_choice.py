import pytest

from kiarina.agi.chat_provider_impl.openai._operations.to_openai_tool_choice import (
    to_openai_tool_choice,
)


@pytest.mark.parametrize(
    ("tool_choice", "expected"),
    [
        (None, "auto"),
        ("auto", "auto"),
        ("any", "required"),
        ("get_weather", "get_weather"),
    ],
)
def test_to_openai_tool_choice(tool_choice: str | None, expected: str) -> None:
    assert to_openai_tool_choice(tool_choice) == expected
