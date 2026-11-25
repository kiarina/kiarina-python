from datetime import datetime
from typing import Literal


class UsageLimitError(RuntimeError):
    """
    The account behind the provider hit a limit of its plan, so the same request
    fails until the limit resets.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        kind: Literal["rate_limit", "usage_limit"] | None = None,
        window: str | None = None,
        resets_at: datetime | None = None,
    ) -> None:
        if message is None:
            message = "A usage limit has been reached."

        # `rate_limit`: too many requests in a short time. `usage_limit`: the
        # plan's allowance for a window is used up. `None`: the vendor did not say.
        self.kind: Literal["rate_limit", "usage_limit"] | None = kind
        # The exhausted window as the vendor names it, such as `five_hour`.
        self.window: str | None = window
        # When the limit resets (timezone-aware), if the vendor reported it.
        self.resets_at: datetime | None = resets_at
        super().__init__(message)
