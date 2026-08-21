import asyncio

from kiarina.lib.firebase import (
    Token,
    TokenManager,
    TokenStore,
)


class InMemoryTokenStore(TokenStore):
    def __init__(self, token: Token) -> None:
        self._token: Token = token
        self.get_count: int = 0

    async def get(self) -> Token:
        self.get_count += 1
        return self._token

    async def set(self, token: Token) -> None:
        self._token = token


async def test_happy_path(api_key: str, token: Token) -> None:
    token_store = InMemoryTokenStore(token)

    manager = TokenManager(
        api_key=api_key,
        token_store=token_store,
    )

    assert await manager.get_token() == token
    assert (await manager.get_token()).id_token == token.id_token

    # The 'exp' claim has one-second resolution
    await asyncio.sleep(1.1)

    new_token = await manager.refresh()
    assert new_token.expires_at > token.expires_at
    assert await token_store.get() == new_token
    assert await manager.get_token() == new_token


async def test_cached_token(api_key: str, token: Token) -> None:
    token_store = InMemoryTokenStore(token)

    manager = TokenManager(
        api_key=api_key,
        token_store=token_store,
    )

    await manager.get_token()
    assert token_store.get_count == 1

    await manager.get_token()
    assert token_store.get_count == 1


async def test_refresh_before_expiration(api_key: str, token: Token) -> None:
    token_store = InMemoryTokenStore(token)

    manager = TokenManager(
        api_key=api_key,
        token_store=token_store,
        refresh_buffer_seconds=7200,
    )

    # The 'exp' claim has one-second resolution
    await asyncio.sleep(1.1)

    new_token = await manager.get_token()
    stored = await token_store.get()
    assert stored.id_token == new_token.id_token
    assert stored.expires_at > token.expires_at
