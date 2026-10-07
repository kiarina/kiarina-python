from typing import Any

import pytest

from kiarina.agi.chat_provider_impl.anthropic._operations.append_tool_choice_instruction import (
    append_tool_choice_instruction,
)


def _messages() -> list[dict[str, Any]]:
    return [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {"role": "system", "content": "Be brief."},
    ]


@pytest.mark.parametrize(
    ("tool_choice", "text"),
    [
        ("any", "You must respond by calling one of the provided tools."),
        ("get_weather", "You must respond by calling the `get_weather` tool."),
    ],
)
def test_append_tool_choice_instruction(tool_choice: str, text: str) -> None:
    messages = _messages()

    append_tool_choice_instruction(messages, tool_choice)

    assert messages[0]["content"][-1] == {"type": "text", "text": text}
    assert messages[1] == {"role": "system", "content": "Be brief."}


@pytest.mark.parametrize("tool_choice", [None, "auto"])
def test_not_forced(tool_choice: str | None) -> None:
    messages = _messages()

    append_tool_choice_instruction(messages, tool_choice)

    assert messages == _messages()
