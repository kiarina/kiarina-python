from datetime import UTC, datetime

from kiarina.agi.chat_provider import UsageLimitError


def test_usage_limit_error() -> None:
    resets_at = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    error = UsageLimitError(
        "limit", kind="usage_limit", window="five_hour", resets_at=resets_at
    )

    assert isinstance(error, RuntimeError)
    assert str(error) == "limit"
    assert (error.kind, error.window, error.resets_at) == (
        "usage_limit",
        "five_hour",
        resets_at,
    )


def test_defaults() -> None:
    error = UsageLimitError()

    assert str(error) == "A usage limit has been reached."
    assert (error.kind, error.window, error.resets_at) == (None, None, None)
