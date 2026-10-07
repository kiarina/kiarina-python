import pytest

from kiarina.agi.chat_provider_impl.openai._operations.from_finish_reason import (
    from_finish_reason,
)


@pytest.mark.parametrize(
    ("finish_reason", "expected"),
    [
        ("stop", "stop"),
        ("tool_calls", "stop"),
        (None, "stop"),
        ("length", "max_tokens"),
        ("content_filter", "content_filter"),
    ],
)
def test_from_finish_reason(finish_reason: str | None, expected: str) -> None:
    assert from_finish_reason(finish_reason) == expected
