import asyncio
from datetime import datetime, timedelta, timezone

from .._schemas.token_data import TokenData
from .._types.token_store import TokenStore
from .._utils.refresh_id_token import refresh_id_token
from .in_memory_token_store import InMemoryTokenStore


class TokenManager:
    def __init__(
        self,
        *,
        api_key: str,
        token_store: TokenStore | TokenData,
        refresh_buffer_seconds: int = 300,
    ) -> None:
        self._api_key = api_key

        self._token_store: TokenStore = (
            InMemoryTokenStore(token_store)
            if isinstance(token_store, TokenData)
            else token_store
        )
        self._refresh_buffer_seconds = refresh_buffer_seconds
        self._token_data: TokenData | None = None
        self._refresh_lock = asyncio.Lock()

    async def get_id_token(self) -> str:
        token_data = self._token_data

        if token_data is None or self._needs_refresh(token_data):
            async with self._refresh_lock:
                token_data = self._token_data

                if token_data is None or self._needs_refresh(token_data):
                    token_data = await self._token_store.get()

                    if self._needs_refresh(token_data):
                        token_data = await self._do_refresh(token_data)

                    self._token_data = token_data

        return token_data.id_token

    async def refresh(self) -> TokenData:
        async with self._refresh_lock:
            token_data = await self._do_refresh(await self._token_store.get())
            self._token_data = token_data
            return token_data

    def _needs_refresh(self, token_data: TokenData) -> bool:
        now = datetime.now(timezone.utc)
        refresh_threshold = token_data.expires_at - timedelta(
            seconds=self._refresh_buffer_seconds
        )

        return now >= refresh_threshold

    async def _do_refresh(self, token_data: TokenData) -> TokenData:
        new_token_data = await refresh_id_token(token_data.refresh_token, self._api_key)
        await self._token_store.set(new_token_data)
        return new_token_data
