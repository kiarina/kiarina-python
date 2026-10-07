import pytest

from kiarina.agi.chat_provider_impl.anthropic._operations.from_stop_reason import (
    from_stop_reason,
)


@pytest.mark.parametrize(
    ("stop_reason", "expected"),
    [
        ("end_turn", "stop"),
        ("tool_use", "stop"),
        (None, "stop"),
        ("max_tokens", "max_tokens"),
        ("model_context_window_exceeded", "max_tokens"),
        ("refusal", "refusal"),
    ],
)
def test_from_stop_reason(stop_reason: str | None, expected: str) -> None:
    assert from_stop_reason(stop_reason) == expected
