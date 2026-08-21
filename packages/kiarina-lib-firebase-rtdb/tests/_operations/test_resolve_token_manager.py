import base64
import json
from collections.abc import Iterator

import pytest

from kiarina.lib.firebase import (
    InMemoryTokenStore,
    Token,
    TokenManager,
    settings_manager as firebase_settings_manager,
    token_manager_registry,
)
from kiarina.lib.firebase_rtdb import settings_manager
from kiarina.lib.firebase_rtdb._operations.resolve_token import resolve_token
from kiarina.lib.firebase_rtdb._operations.resolve_token_manager import (
    resolve_token_manager,
)


def make_token(uid: str) -> Token:
    payload = {"exp": 4102444800, "sub": uid, "aud": "project_1"}
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return Token(refresh_token="refresh-token", id_token=f"header.{segment}.signature")


def make_manager(uid: str) -> TokenManager:
    return TokenManager(
        api_key="api-key",
        token_store=InMemoryTokenStore(make_token(uid)),
    )


@pytest.fixture
def token_manager() -> Iterator[TokenManager]:
    manager = make_manager("registry_user")

    token_manager_registry.register("rtdb", manager)
    settings_manager.user_config = {"firebase_settings_key": "rtdb"}

    yield manager

    settings_manager.user_config = {}
    token_manager_registry.clear()


def test_explicit_token_manager_wins(token_manager: TokenManager) -> None:
    other = make_manager("other_user")
    assert resolve_token_manager(other) is other


def test_token_manager_from_registry(token_manager: TokenManager) -> None:
    assert resolve_token_manager() is token_manager


async def test_token_from_registry(token_manager: TokenManager) -> None:
    assert (await resolve_token()).uid == "registry_user"


async def test_explicit_token_wins(token_manager: TokenManager) -> None:
    explicit = make_token("explicit_user")
    assert await resolve_token(explicit) is explicit


@pytest.fixture
def default_token_manager() -> Iterator[TokenManager]:
    manager = make_manager("default_user")

    firebase_user_config = firebase_settings_manager.user_config
    firebase_settings_manager.user_config = {"configs": {"default": {"api_key": "k"}}}
    token_manager_registry.register("default", manager)
    settings_manager.user_config = {}

    yield manager

    settings_manager.user_config = {}
    firebase_settings_manager.user_config = firebase_user_config
    token_manager_registry.clear()


def test_name_is_not_configured(default_token_manager: TokenManager) -> None:
    assert resolve_token_manager() is default_token_manager


async def test_token_without_a_name(default_token_manager: TokenManager) -> None:
    assert (await resolve_token()).uid == "default_user"
