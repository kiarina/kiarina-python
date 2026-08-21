import base64
import json
from pathlib import Path

import pytest

from kiarina.lib.firebase import FileTokenStore, Token


@pytest.fixture
def token() -> Token:
    payload = {"exp": 4102444800, "sub": "user_1", "aud": "project_1"}
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return Token(refresh_token="refresh-token", id_token=f"header.{segment}.signature")


async def test_round_trip(tmp_path: Path, token: Token) -> None:
    store = FileTokenStore(str(tmp_path / "token.json"))
    await store.set(token)

    assert await store.get() == token


async def test_file_not_found(tmp_path: Path) -> None:
    store = FileTokenStore(str(tmp_path / "missing.json"))

    with pytest.raises(FileNotFoundError):
        await store.get()
