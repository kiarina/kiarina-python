import base64
import json
from datetime import datetime, timezone

import pytest

from kiarina.lib.firebase import TokenData


def make_id_token(payload: object) -> str:
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return f"header.{segment}.signature"


def test_from_api_response() -> None:
    expires_at = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)

    token_data = TokenData.from_api_response(
        id_token=make_id_token({"exp": int(expires_at.timestamp())}),
        refresh_token="refresh_token",
    )

    assert token_data.expires_at == expires_at


@pytest.mark.parametrize(
    "id_token",
    [
        "not_a_jwt",
        "header.!!!.signature",
        make_id_token({}),
        make_id_token({"exp": "3600"}),
    ],
)
def test_invalid_id_token(id_token: str) -> None:
    with pytest.raises(ValueError):
        TokenData.from_api_response(
            id_token=id_token,
            refresh_token="refresh_token",
        )


def test_uid() -> None:
    expires_at = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)

    token_data = TokenData.from_api_response(
        id_token=make_id_token({"exp": int(expires_at.timestamp()), "sub": "user_1"}),
        refresh_token="refresh_token",
    )

    assert token_data.uid == "user_1"


@pytest.mark.parametrize("sub", [None, 1])
def test_invalid_uid(sub: object) -> None:
    payload: dict[str, object] = {"exp": 3600}

    if sub is not None:
        payload["sub"] = sub

    token_data = TokenData(
        refresh_token="refresh_token",
        id_token=make_id_token(payload),
        expires_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError):
        _ = token_data.uid
