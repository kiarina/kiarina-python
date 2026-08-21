import base64
import json
from datetime import datetime, timezone

import pytest

from kiarina.lib.firebase import Token


def make_id_token(payload: object) -> str:
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return f"header.{segment}.signature"


def make_token(payload: object) -> Token:
    return Token(refresh_token="refresh_token", id_token=make_id_token(payload))


def test_claims() -> None:
    expires_at = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)

    token = make_token(
        {
            "exp": int(expires_at.timestamp()),
            "sub": "user_1",
            "aud": "project_1",
        }
    )

    assert token.expires_at == expires_at
    assert token.uid == "user_1"
    assert token.project_id == "project_1"


@pytest.mark.parametrize(
    "id_token",
    [
        "not_a_jwt",
        "header.!!!.signature",
        make_id_token({}),
        make_id_token({"exp": "3600"}),
    ],
)
def test_invalid_expires_at(id_token: str) -> None:
    with pytest.raises(ValueError):
        _ = Token(refresh_token="refresh_token", id_token=id_token).expires_at


@pytest.mark.parametrize("payload", [{}, {"sub": 1}])
def test_invalid_uid(payload: object) -> None:
    with pytest.raises(ValueError):
        _ = make_token(payload).uid


@pytest.mark.parametrize("payload", [{}, {"aud": 1}])
def test_invalid_project_id(payload: object) -> None:
    with pytest.raises(ValueError):
        _ = make_token(payload).project_id


def test_old_token_file_shape_is_accepted() -> None:
    token = Token.model_validate(
        {
            "refresh_token": "refresh_token",
            "id_token": make_id_token({"exp": 3600}),
            "expires_at": "2026-01-01T00:00:00Z",
        }
    )

    assert token.model_dump() == {
        "refresh_token": "refresh_token",
        "id_token": token.id_token,
    }
