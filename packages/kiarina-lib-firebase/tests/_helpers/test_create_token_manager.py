import base64
import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from kiarina.lib.firebase import (
    FileTokenStore,
    Token,
    create_token_manager,
    settings_manager,
)


@pytest.fixture(autouse=True)
def isolated_settings() -> Iterator[None]:
    user_config = settings_manager.user_config
    yield
    settings_manager.user_config = user_config


@pytest.fixture
def token() -> Token:
    payload = {"exp": 4102444800, "sub": "user_1", "aud": "project_1"}
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return Token(refresh_token="refresh-token", id_token=f"header.{segment}.signature")


def configure(**overrides: object) -> None:
    settings_manager.user_config = {
        "configs": {
            "development": {"api_key": "dk", **overrides},
            "production": {"api_key": "pk", **overrides},
        },
        "default": "production",
    }


async def test_token_argument(token: Token) -> None:
    configure()

    manager = create_token_manager(token_store=token)

    assert await manager.get_token() == token


async def test_token_file_from_settings(tmp_path: Path, token: Token) -> None:
    token_file = tmp_path / "token.json"
    await FileTokenStore(str(token_file)).set(token)

    configure(token_file_path=str(token_file))

    assert await create_token_manager().get_token() == token


async def test_settings_key(tmp_path: Path, token: Token) -> None:
    token_file = tmp_path / "token.json"
    await FileTokenStore(str(token_file)).set(token)

    configure()
    settings_manager.user_config = {
        "configs": {
            "development": {
                "api_key": "dk",
                "token_file_path": str(token_file),
            },
            "production": {"api_key": "pk"},
        },
        "default": "production",
    }

    assert await create_token_manager("development").get_token() == token

    with pytest.raises(ValueError, match="'token_store' is required"):
        create_token_manager("production")
