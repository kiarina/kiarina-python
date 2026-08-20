from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kiarina.lib.firebase import (
    TokenData,
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
def token_data() -> TokenData:
    return TokenData(
        refresh_token="refresh-token",
        id_token="id-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


def configure(**overrides: object) -> None:
    settings_manager.user_config = {
        "configs": {
            "development": {"project_id": "d", "api_key": "dk", **overrides},
            "production": {"project_id": "p", "api_key": "pk", **overrides},
        },
        "default": "production",
        "aliases": {"prod": "production"},
    }


def test_registered_instance_wins(token_data: TokenData) -> None:
    configure()
    manager = TokenManager(api_key="api-key", token_store=token_data)
    token_manager_registry.register("production", manager)

    assert token_manager_registry.get("production") is manager
    assert token_manager_registry.get() is manager


def test_created_from_settings(tmp_path: Path) -> None:
    configure(token_data_file_path=str(tmp_path / "token.json"))

    manager = token_manager_registry.get()

    assert isinstance(manager, TokenManager)
    assert token_manager_registry.get() is manager
    assert token_manager_registry.get("prod") is manager
    assert token_manager_registry.get("development") is not manager


def test_active_key_selects_the_settings(tmp_path: Path) -> None:
    configure(token_data_file_path=str(tmp_path / "token.json"))
    settings_manager.active_key = "development"

    assert token_manager_registry.get() is token_manager_registry.get("development")


def test_token_data_file_path_is_not_configured() -> None:
    configure()

    with pytest.raises(
        ValueError, match="'token_data_file_path' is not configured in the 'production'"
    ):
        token_manager_registry.get()


def test_unknown_name() -> None:
    configure()

    with pytest.raises(ValueError, match="TokenManager config is not configured"):
        token_manager_registry.get("unknown")
