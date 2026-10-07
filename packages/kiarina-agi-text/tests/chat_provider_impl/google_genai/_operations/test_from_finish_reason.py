import pytest

from kiarina.agi.chat_provider_impl.google_genai._operations.from_finish_reason import (
    from_finish_reason,
)


@pytest.mark.parametrize(
    ("finish_reason", "expected"),
    [
        ("STOP", "stop"),
        (None, "stop"),
        ("MALFORMED_FUNCTION_CALL", "stop"),
        ("MAX_TOKENS", "max_tokens"),
        ("SAFETY", "safety"),
        ("PROHIBITED_CONTENT", "safety"),
        ("BLOCKLIST", "safety"),
        ("SPII", "safety"),
        ("RECITATION", "safety"),
    ],
)
def test_from_finish_reason(finish_reason: str | None, expected: str) -> None:
    assert from_finish_reason(finish_reason) == expected


def test_prompt_blocked() -> None:
    assert from_finish_reason(None, prompt_blocked=True) == "safety"
