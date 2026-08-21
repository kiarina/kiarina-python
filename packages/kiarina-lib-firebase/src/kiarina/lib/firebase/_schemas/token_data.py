import base64
import binascii
import json
from datetime import datetime, timezone
from typing import Any, Self

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

    @property
    def uid(self) -> str:
        return _get_uid(self.id_token)

    @classmethod
    def from_api_response(cls, id_token: str, refresh_token: str) -> Self:
        return cls(
            refresh_token=refresh_token,
            id_token=id_token,
            expires_at=_get_expires_at(id_token),
        )


def _get_expires_at(id_token: str) -> datetime:
    exp = _get_claim(id_token, "exp")

    if not isinstance(exp, (int, float)) or isinstance(exp, bool):
        raise ValueError("The 'exp' claim in id_token is not a number")

    return datetime.fromtimestamp(exp, tz=timezone.utc)


def _get_uid(id_token: str) -> str:
    sub = _get_claim(id_token, "sub")

    if not isinstance(sub, str):
        raise ValueError("The 'sub' claim in id_token is not a string")

    return sub


def _get_claim(id_token: str, name: str) -> Any:
    try:
        payload_segment = id_token.split(".")[1]
        padding = "=" * (-len(payload_segment) % 4)
        payload: Any = json.loads(
            base64.urlsafe_b64decode(payload_segment + padding).decode("utf-8")
        )
        return payload[name]
    except (
        IndexError,
        KeyError,
        TypeError,
        ValueError,
        binascii.Error,
        UnicodeDecodeError,
    ) as e:
        raise ValueError(f"Failed to read the '{name}' claim from id_token") from e
