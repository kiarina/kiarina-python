import asyncio

import pytest

from kiarina.lib.firebase import (
    TokenData,
    TokenDataCache,
    TokenManager,
)


class InMemoryTokenCache(TokenDataCache):
    def __init__(self, token_data: TokenData) -> None:
        self._token_data: TokenData = token_data

    async def get(self) -> TokenData:
        return self._token_data

    async def set(self, token_data: TokenData) -> None:
        self._token_data = token_data


async def test_missing_parameters() -> None:
    with pytest.raises(
        ValueError,
        match="At least one of 'refresh_token', 'token_data', or 'token_data_cache'",
    ):
        TokenManager(api_key="test")


async def test_before_get_id_token(api_key: str, token_data: TokenData) -> None:
    manager = TokenManager(
        api_key=api_key,
        token_data_cache=InMemoryTokenCache(token_data),
    )

    with pytest.raises(AssertionError, match="Refresh token is not set\\."):
        _ = manager.refresh_token

    with pytest.raises(AssertionError, match="Token data is not set\\."):
        _ = manager.token_data


async def test_happy_path(api_key: str, token_data: TokenData) -> None:
    manager = TokenManager(
        api_key=api_key,
        token_data_cache=InMemoryTokenCache(token_data),
    )

    id_token = await manager.get_id_token()
    expires_at = manager.expires_at
    assert id_token == manager.id_token

    id_token_2 = await manager.get_id_token()
    assert id_token_2 == id_token
    assert manager.expires_at == expires_at

    await asyncio.sleep(0.1)

    new_token_data = await manager.refresh()
    assert manager.expires_at > expires_at
    assert new_token_data.expires_at == manager.expires_at


async def test_need_refresh(api_key: str, token_data: TokenData) -> None:
    manager = TokenManager(
        api_key=api_key,
        refresh_token=token_data.refresh_token,
    )

    await manager.get_id_token()


async def test_init_with_token_data(api_key: str, token_data: TokenData) -> None:
    TokenManager(
        api_key=api_key,
        token_data=token_data,
    )
