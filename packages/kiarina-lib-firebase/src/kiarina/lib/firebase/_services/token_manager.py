import asyncio
from datetime import datetime, timedelta, timezone

from .._helpers.refresh_id_token import refresh_id_token
from .._schemas.token import Token
from .._types.token_store import TokenStore


class TokenManager:
    def __init__(
        self,
        *,
        api_key: str,
        token_store: TokenStore,
        refresh_buffer_seconds: int = 300,
    ) -> None:
        self._api_key = api_key
        self._token_store = token_store
        self._refresh_buffer_seconds = refresh_buffer_seconds
        self._token: Token | None = None
        self._refresh_lock = asyncio.Lock()

    async def get_token(self) -> Token:
        token = self._token

        if token is None or self._needs_refresh(token):
            async with self._refresh_lock:
                token = self._token

                if token is None or self._needs_refresh(token):
                    token = await self._token_store.get()

                    if self._needs_refresh(token):
                        token = await self._do_refresh(token)

                    self._token = token

        return token

    async def refresh(self) -> Token:
        async with self._refresh_lock:
            token = await self._do_refresh(await self._token_store.get())
            self._token = token
            return token

    def _needs_refresh(self, token: Token) -> bool:
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=self._refresh_buffer_seconds
        )

        return now >= refresh_threshold

    async def _do_refresh(self, token: Token) -> Token:
        new_token = await refresh_id_token(token, self._api_key)
        await self._token_store.set(new_token)
        return new_token
