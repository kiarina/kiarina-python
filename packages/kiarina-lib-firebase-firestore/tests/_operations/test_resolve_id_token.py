from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import pytest

from kiarina.lib.firebase import (
    TokenData,
    TokenManager,
    settings_manager as firebase_settings_manager,
    token_manager_registry,
)
from kiarina.lib.firebase_firestore import settings_manager
from kiarina.lib.firebase_firestore._operations.resolve_id_token import (
    resolve_id_token,
)


@pytest.fixture
def registered_token_manager() -> Iterator[None]:
    token_data = TokenData(
        refresh_token="refresh-token",
        id_token="registry-id-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    token_manager_registry.register(
        "firestore",
        TokenManager(api_key="api-key", token_store=token_data),
    )
    settings_manager.user_config = {"firebase_settings_key": "firestore"}

    yield

    settings_manager.user_config = {}
    token_manager_registry.clear()


async def test_id_token_from_registry(registered_token_manager: None) -> None:
    assert await resolve_id_token() == "registry-id-token"


async def test_explicit_id_token_wins(registered_token_manager: None) -> None:
    assert await resolve_id_token("explicit-id-token") == "explicit-id-token"


@pytest.fixture
def default_token_manager() -> Iterator[None]:
    token_data = TokenData(
        refresh_token="refresh-token",
        id_token="default-id-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    firebase_user_config = firebase_settings_manager.user_config
    firebase_settings_manager.user_config = {
        "configs": {"default": {"project_id": "p", "api_key": "k"}}
    }
    token_manager_registry.register(
        "default",
        TokenManager(api_key="api-key", token_store=token_data),
    )
    settings_manager.user_config = {}

    yield

    settings_manager.user_config = {}
    firebase_settings_manager.user_config = firebase_user_config
    token_manager_registry.clear()


async def test_name_is_not_configured(default_token_manager: None) -> None:
    assert await resolve_id_token() == "default-id-token"
