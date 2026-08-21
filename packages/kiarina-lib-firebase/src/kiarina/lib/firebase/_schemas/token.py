import base64
import binascii
import json
from datetime import datetime, timezone
from functools import cached_property
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """Firebase authentication token set."""

    model_config = ConfigDict(frozen=True)

    refresh_token: str = Field(
        title="Refresh token",
        description="Token used to obtain a new ID token.",
    )
    id_token: str = Field(
        title="ID token",
        description="Firebase ID token.",
    )

    @cached_property
    def project_id(self) -> str:
        aud = _get_claim(self.id_token, "aud")

        if not isinstance(aud, str):
            raise ValueError("The 'aud' claim in id_token is not a string")

        return aud

    @cached_property
    def uid(self) -> str:
        sub = _get_claim(self.id_token, "sub")

        if not isinstance(sub, str):
            raise ValueError("The 'sub' claim in id_token is not a string")

        return sub

    @cached_property
    def expires_at(self) -> datetime:
        exp = _get_claim(self.id_token, "exp")

        if not isinstance(exp, (int, float)) or isinstance(exp, bool):
            raise ValueError("The 'exp' claim in id_token is not a number")

        return datetime.fromtimestamp(exp, tz=timezone.utc)


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
