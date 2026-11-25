from datetime import UTC, datetime
from typing import Any

import pytest

from kiarina.agi.chat_provider_impl.codex._operations.to_usage_limit_error import (
    to_usage_limit_error,
)

_FIVE_HOUR = {"usedPercent": 100, "windowDurationMins": 300, "resetsAt": 1_800_000_000}
_SEVEN_DAY = {
    "usedPercent": 100,
    "windowDurationMins": 10080,
    "resetsAt": 1_800_500_000,
}
_OPEN = {"usedPercent": 40, "windowDurationMins": 10080, "resetsAt": 1_800_900_000}


@pytest.mark.parametrize(
    ("code", "rate_limits", "expected"),
    [
        (
            "usageLimitExceeded",
            [{"primary": _FIVE_HOUR, "secondary": _OPEN}],
            ("usage_limit", "five_hour", 1_800_000_000),
        ),
        (
            "usageLimitExceeded",
            [{"primary": _FIVE_HOUR}, {"limitId": "x", "secondary": _SEVEN_DAY}],
            ("usage_limit", "seven_day", 1_800_500_000),
        ),
        (
            "usageLimitExceeded",
            [{"primary": {**_FIVE_HOUR, "windowDurationMins": 60}}],
            ("usage_limit", "60_minutes", 1_800_000_000),
        ),
        (
            "usageLimitExceeded",
            [{"primary": {"usedPercent": 100, "resetsAt": 1_800_000_000}}],
            ("usage_limit", None, 1_800_000_000),
        ),
        (
            "usageLimitExceeded",
            [{"primary": _OPEN, "secondary": {"usedPercent": 100, "resetsAt": None}}],
            ("usage_limit", None, None),
        ),
        ("usageLimitExceeded", [], ("usage_limit", None, None)),
        ("rateLimitExceeded", [{"primary": _FIVE_HOUR}], ("rate_limit", None, None)),
    ],
)
def test_limit(
    code: str,
    rate_limits: list[dict[str, Any]],
    expected: tuple[str, str | None, int | None],
) -> None:
    error = to_usage_limit_error(
        "Codex failed: x", {"codexErrorInfo": code}, rate_limits
    )

    assert error is not None
    assert str(error) == "Codex failed: x"
    kind, window, resets_at = expected
    assert (error.kind, error.window) == (kind, window)
    assert error.resets_at == (
        datetime.fromtimestamp(resets_at, tz=UTC) if resets_at else None
    )


@pytest.mark.parametrize(
    "error",
    [
        {"message": "You've hit your usage limit."},
        {"codexErrorInfo": "serverOverloaded"},
        {"codexErrorInfo": {"httpConnectionFailed": {"httpStatusCode": 429}}},
    ],
)
def test_not_a_limit(error: dict[str, Any]) -> None:
    assert to_usage_limit_error("x", error, [{"primary": _FIVE_HOUR}]) is None
