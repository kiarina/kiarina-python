from datetime import UTC, datetime

from claude_agent_sdk import RateLimitInfo, ResultMessage

from kiarina.agi.chat_provider import UsageLimitError


def to_usage_limit_error(
    message: str,
    result_message: ResultMessage,
    *,
    assistant_errors: list[str],
    rate_limit_info: RateLimitInfo | None,
) -> UsageLimitError | None:
    """
    An error result as a `UsageLimitError`, or `None` when nothing structured
    marks a limit: an assistant message with the `rate_limit` error, a `429`
    from the API, or a `rejected` rate limit event with no overage to fall back
    on. The text of the result is not read.
    """
    rejected = rate_limit_info if _is_rejected(rate_limit_info) else None

    if not (
        "rate_limit" in assistant_errors
        or result_message.api_error_status == 429
        or (rejected and rejected.overage_status in (None, "rejected"))
    ):
        return None

    if rejected is None:
        return UsageLimitError(message)

    resets_at = rejected.resets_at

    if rejected.rate_limit_type == "overage" and rejected.overage_resets_at:
        resets_at = rejected.overage_resets_at

    return UsageLimitError(
        message,
        kind="usage_limit",
        window=rejected.rate_limit_type,
        resets_at=datetime.fromtimestamp(resets_at, tz=UTC) if resets_at else None,
    )


def _is_rejected(rate_limit_info: RateLimitInfo | None) -> bool:
    return rate_limit_info is not None and rate_limit_info.status == "rejected"
