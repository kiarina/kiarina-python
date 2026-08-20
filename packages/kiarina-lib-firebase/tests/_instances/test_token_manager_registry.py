from collections.abc import Iterator

import pytest

from kiarina.lib.firebase import (
    TokenData,
    TokenManager,
    token_manager_registry,
)


@pytest.fixture(autouse=True)
def clear_registry() -> Iterator[None]:
    token_manager_registry.clear()
    yield
    token_manager_registry.clear()


def test_register_and_get(api_key: str, token_data: TokenData) -> None:
    manager = TokenManager(api_key=api_key, token_store=token_data)
    token_manager_registry.register("primary", manager)

    assert token_manager_registry.get("primary") is manager
    assert token_manager_registry.is_registered("primary")
    assert token_manager_registry.list_names() == ["primary"]


def test_unregistered_name() -> None:
    with pytest.raises(ValueError, match="TokenManager config is not configured"):
        token_manager_registry.get("unknown")


def test_name_is_required() -> None:
    with pytest.raises(ValueError, match="Default is not configured"):
        token_manager_registry.get()
