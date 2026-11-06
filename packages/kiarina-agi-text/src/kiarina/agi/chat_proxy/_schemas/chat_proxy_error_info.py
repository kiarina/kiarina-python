from typing import Literal, Self

from pydantic import BaseModel, Field

from kiarina.agi.chat_provider import MaxTokenError, SafetyError, TokenOverflowError

from .._exceptions.chat_proxy_error import ChatProxyError


class ChatProxyErrorInfo(BaseModel):
    """An error raised on the chat proxy, carried back to be raised again by the caller."""

    kind: Literal["safety", "max_token", "token_overflow", "other"] = Field(
        title="Kind", description="Which chat provider error it was."
    )
    error_type: str = Field(
        title="Error Type", description="The exception's class name."
    )
    message: str = Field(title="Message", description="The exception's message.")
    category: str | None = Field(
        default=None, title="Category", description="`SafetyError.category`."
    )
    request_id: str | None = Field(
        default=None, title="Request ID", description="`SafetyError.request_id`."
    )
    token_count: int | None = Field(
        default=None,
        title="Token Count",
        description="`TokenOverflowError.token_count`.",
    )
    limit: int | None = Field(
        default=None, title="Limit", description="`TokenOverflowError.limit`."
    )

    @classmethod
    def from_exception(cls, error: BaseException) -> Self:
        error_type = type(error).__name__
        message = str(error)

        if isinstance(error, SafetyError):
            return cls(
                kind="safety",
                error_type=error_type,
                message=message,
                category=error.category,
                request_id=error.request_id,
            )

        if isinstance(error, MaxTokenError):
            return cls(kind="max_token", error_type=error_type, message=message)

        if isinstance(error, TokenOverflowError):
            return cls(
                kind="token_overflow",
                error_type=error_type,
                message=message,
                token_count=error.token_count,
                limit=error.limit,
            )

        return cls(kind="other", error_type=error_type, message=message)

    def to_exception(self) -> Exception:
        if self.kind == "safety":
            return SafetyError(
                self.message, category=self.category, request_id=self.request_id
            )

        if self.kind == "max_token":
            return MaxTokenError(self.message)

        if self.kind == "token_overflow":
            return TokenOverflowError(self.token_count or 0, limit=self.limit)

        return ChatProxyError(f"{self.error_type}: {self.message}")
