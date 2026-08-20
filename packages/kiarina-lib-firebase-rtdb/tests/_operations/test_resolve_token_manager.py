from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import pytest

from kiarina.lib.firebase import (
    TokenData,
    TokenManager,
    settings_manager as firebase_settings_manager,
    token_manager_registry,
)
from kiarina.lib.firebase_rtdb import settings_manager
from kiarina.lib.firebase_rtdb._operations.resolve_id_token import resolve_id_token
from kiarina.lib.firebase_rtdb._operations.resolve_token_manager import (
    resolve_token_manager,
)


@pytest.fixture
def token_manager() -> Iterator[TokenManager]:
    token_data = TokenData(
        refresh_token="refresh-token",
        id_token="registry-id-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    manager = TokenManager(api_key="api-key", token_store=token_data)

    token_manager_registry.register("rtdb", manager)
    settings_manager.user_config = {"firebase_token_manager_name": "rtdb"}

    yield manager

    settings_manager.user_config = {}
    token_manager_registry.clear()


def test_explicit_token_manager_wins(token_manager: TokenManager) -> None:
    other = TokenManager(
        api_key="api-key",
        token_store=TokenData(
            refresh_token="other-refresh-token",
            id_token="other-id-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ),
    )
    assert resolve_token_manager(other) is other


def test_token_manager_from_registry(token_manager: TokenManager) -> None:
    assert resolve_token_manager() is token_manager


async def test_id_token_from_registry(token_manager: TokenManager) -> None:
    assert await resolve_id_token() == "registry-id-token"


async def test_explicit_id_token_wins(token_manager: TokenManager) -> None:
    assert await resolve_id_token("explicit-id-token") == "explicit-id-token"


@pytest.fixture
def default_token_manager() -> Iterator[TokenManager]:
    token_data = TokenData(
        refresh_token="refresh-token",
        id_token="default-id-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    manager = TokenManager(api_key="api-key", token_store=token_data)

    firebase_user_config = firebase_settings_manager.user_config
    firebase_settings_manager.user_config = {
        "configs": {"default": {"project_id": "p", "api_key": "k"}}
    }
    token_manager_registry.register("default", manager)
    settings_manager.user_config = {}

    yield manager

    settings_manager.user_config = {}
    firebase_settings_manager.user_config = firebase_user_config
    token_manager_registry.clear()


def test_name_is_not_configured(default_token_manager: TokenManager) -> None:
    assert resolve_token_manager() is default_token_manager


async def test_id_token_without_a_name(default_token_manager: TokenManager) -> None:
    assert await resolve_id_token() == "default-id-token"
