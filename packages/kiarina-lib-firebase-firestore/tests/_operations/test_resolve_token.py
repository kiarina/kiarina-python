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
from kiarina.lib.firebase_firestore import settings_manager
from kiarina.lib.firebase_firestore._operations.resolve_token import resolve_token


def make_token(uid: str) -> Token:
    payload = {"exp": 4102444800, "sub": uid, "aud": "project_1"}
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return Token(refresh_token="refresh-token", id_token=f"header.{segment}.signature")


def register(name: str, uid: str) -> None:
    token_manager_registry.register(
        name,
        TokenManager(
            api_key="api-key", token_store=InMemoryTokenStore(make_token(uid))
        ),
    )


@pytest.fixture
def registered_token_manager() -> Iterator[None]:
    register("firestore", "registry_user")
    settings_manager.user_config = {"firebase_settings_key": "firestore"}

    yield

    settings_manager.user_config = {}
    token_manager_registry.clear()


async def test_token_from_registry(registered_token_manager: None) -> None:
    assert (await resolve_token()).uid == "registry_user"


async def test_explicit_token_wins(registered_token_manager: None) -> None:
    explicit = make_token("explicit_user")
    assert await resolve_token(explicit) is explicit


@pytest.fixture
def default_token_manager() -> Iterator[None]:
    firebase_user_config = firebase_settings_manager.user_config
    firebase_settings_manager.user_config = {"configs": {"default": {"api_key": "k"}}}
    register("default", "default_user")
    settings_manager.user_config = {}

    yield

    settings_manager.user_config = {}
    firebase_settings_manager.user_config = firebase_user_config
    token_manager_registry.clear()


async def test_name_is_not_configured(default_token_manager: None) -> None:
    assert (await resolve_token()).uid == "default_user"
