import base64
import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from kiarina.lib.firebase import (
    FileTokenStore,
    InMemoryTokenStore,
    Token,
    TokenManager,
    settings_manager,
    token_manager_registry,
)


@pytest.fixture(autouse=True)
def isolated_registry() -> Iterator[None]:
    user_config = settings_manager.user_config
    token_manager_registry.clear()

    yield

    token_manager_registry.clear()
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
        "aliases": {"prod": "production"},
    }


def test_registered_instance_wins(token: Token) -> None:
    configure()
    manager = TokenManager(api_key="api-key", token_store=InMemoryTokenStore(token))
    token_manager_registry.register("production", manager)

    assert token_manager_registry.get("production") is manager
    assert token_manager_registry.get() is manager


def test_created_from_settings(tmp_path: Path) -> None:
    configure(token_file_path=str(tmp_path / "token.json"))

    manager = token_manager_registry.get()

    assert isinstance(manager, TokenManager)
    assert token_manager_registry.get() is manager
    assert token_manager_registry.get("prod") is manager
    assert token_manager_registry.get("development") is not manager


def test_active_key_selects_the_settings(tmp_path: Path) -> None:
    configure(token_file_path=str(tmp_path / "token.json"))
    settings_manager.active_key = "development"

    assert token_manager_registry.get() is token_manager_registry.get("development")


async def test_token_is_read_from_the_configured_file(
    tmp_path: Path, token: Token
) -> None:
    token_file = tmp_path / "token.json"
    await FileTokenStore(str(token_file)).set(token)

    configure(token_file_path=str(token_file))

    assert await token_manager_registry.get().get_token() == token


def test_token_file_path_is_not_configured() -> None:
    configure()

    with pytest.raises(ValueError, match="'token_store' is required"):
        token_manager_registry.get()


def test_unknown_name() -> None:
    configure()

    with pytest.raises(ValueError, match="TokenManager config is not configured"):
        token_manager_registry.get("unknown")
