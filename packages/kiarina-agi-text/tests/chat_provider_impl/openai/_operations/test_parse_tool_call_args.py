import pytest

from kiarina.agi.chat_provider_impl.openai._operations.parse_tool_call_args import (
    parse_tool_call_args,
)


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (None, {}),
        ("", {}),
        ('{"a": 1}', {"a": 1}),
        ("{broken", {}),
        ("[1, 2]", {}),
    ],
)
def test_parse_tool_call_args(arguments: str | None, expected: dict[str, int]) -> None:
    assert parse_tool_call_args(arguments) == expected
