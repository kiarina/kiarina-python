import asyncio

from kiarina.lib.firebase import (
    TokenData,
    TokenManager,
    TokenStore,
)


class InMemoryTokenStore(TokenStore):
    def __init__(self, token_data: TokenData) -> None:
        self._token_data: TokenData = token_data
        self.get_count: int = 0

    async def get(self) -> TokenData:
        self.get_count += 1
        return self._token_data

    async def set(self, token_data: TokenData) -> None:
        self._token_data = token_data


async def test_happy_path(api_key: str, token_data: TokenData) -> None:
    token_store = InMemoryTokenStore(token_data)

    manager = TokenManager(
        api_key=api_key,
        token_store=token_store,
    )

    id_token = await manager.get_id_token()
    assert id_token == token_data.id_token
    assert await manager.get_id_token() == id_token

    # The 'exp' claim has one-second resolution
    await asyncio.sleep(1.1)

    new_token_data = await manager.refresh()
    assert new_token_data.expires_at > token_data.expires_at
    assert await token_store.get() == new_token_data
    assert await manager.get_id_token() == new_token_data.id_token


async def test_cached_token_data(api_key: str, token_data: TokenData) -> None:
    token_store = InMemoryTokenStore(token_data)

    manager = TokenManager(
        api_key=api_key,
        token_store=token_store,
    )

    await manager.get_id_token()
    assert token_store.get_count == 1

    await manager.get_id_token()
    assert token_store.get_count == 1


async def test_refresh_before_expiration(api_key: str, token_data: TokenData) -> None:
    token_store = InMemoryTokenStore(token_data)

    manager = TokenManager(
        api_key=api_key,
        token_store=token_store,
        refresh_buffer_seconds=7200,
    )

    # The 'exp' claim has one-second resolution
    await asyncio.sleep(1.1)

    id_token = await manager.get_id_token()
    stored = await token_store.get()
    assert stored.id_token == id_token
    assert stored.expires_at > token_data.expires_at


async def test_init_with_token_data(api_key: str, token_data: TokenData) -> None:
    manager = TokenManager(
        api_key=api_key,
        token_store=token_data,
    )

    assert await manager.get_id_token() == token_data.id_token
