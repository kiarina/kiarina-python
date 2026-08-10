from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field


class TokenData(BaseModel):
    """Firebase authentication token data."""

    refresh_token: str = Field(
        title="Refresh token",
        description="Token used to obtain a new ID token.",
    )
    id_token: str = Field(
        title="ID token",
        description="Firebase ID token.",
    )
    expires_at: datetime = Field(
        title="Expiration time",
        description="ID token expiration time in UTC.",
    )

    @classmethod
    def from_api_response(
        cls,
        id_token: str,
        refresh_token: str,
        expires_in: int,
        *,
        issued_at: datetime | None = None,
    ) -> "TokenData":
        if issued_at is None:
            issued_at = datetime.now(timezone.utc)

        return cls(
            refresh_token=refresh_token,
            id_token=id_token,
            expires_at=issued_at + timedelta(seconds=expires_in),
        )
