from datetime import UTC, datetime
from typing import Any, Literal

from kiarina.agi.chat_provider import UsageLimitError

_KINDS: dict[str, Literal["rate_limit", "usage_limit"]] = {
    "rateLimitExceeded": "rate_limit",
    "usageLimitExceeded": "usage_limit",
}

_WINDOW_NAMES = {300: "five_hour", 10080: "seven_day"}


def to_usage_limit_error(
    message: str, error: dict[str, Any], rate_limits: list[dict[str, Any]]
) -> UsageLimitError | None:
    """
    A turn error as a `UsageLimitError`, or `None` when `codexErrorInfo` does not
    name a limit. The error has no reset time, so it comes from the exhausted
    window of the account's rate limit snapshots (`RateLimitSnapshot`).
    """
    code = error.get("codexErrorInfo")
    kind = _KINDS.get(code) if isinstance(code, str) else None

    if kind is None:
        return None

    window = _find_exhausted_window(rate_limits) if kind == "usage_limit" else None

    if window is None:
        return UsageLimitError(message, kind=kind)

    minutes = window.get("windowDurationMins")

    return UsageLimitError(
        message,
        kind=kind,
        window=_WINDOW_NAMES.get(minutes, f"{minutes}_minutes") if minutes else None,
        resets_at=datetime.fromtimestamp(window["resetsAt"], tz=UTC),
    )


def _find_exhausted_window(rate_limits: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The used-up window that resets last: the limit holds until all of them reset."""
    windows = [
        window
        for snapshot in rate_limits
        for key in ("primary", "secondary")
        if isinstance(window := snapshot.get(key), dict)
        and (window.get("usedPercent") or 0) >= 100
        and isinstance(window.get("resetsAt"), int)
    ]
    return max(windows, key=lambda window: window["resetsAt"], default=None)
