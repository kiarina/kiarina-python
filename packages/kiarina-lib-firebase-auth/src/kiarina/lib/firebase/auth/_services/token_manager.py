import asyncio
from datetime import datetime, timedelta, timezone

from .._schemas.token_data import TokenData
from .._utils.refresh_id_token import refresh_id_token


class TokenManager:
    """
    Service class for automatic ID token lifecycle management.

    Automatically refreshes ID tokens before expiration with thread-safe operations.
    """

    def __init__(
        self,
        refresh_token: str,
        api_key: str,
        *,
        token_data: TokenData | None = None,
        refresh_buffer_seconds: int = 300,
    ):
        self.refresh_token: str = refresh_token
        self.api_key: str = api_key
        self._id_token: str | None = token_data.id_token if token_data else None
        self._expires_at: datetime | None = (
            token_data.expires_at if token_data else None
        )
        self._refresh_buffer_seconds = refresh_buffer_seconds
        self._refresh_lock = asyncio.Lock()

    @property
    def id_token(self) -> str:
        if self._id_token is None:  # pragma: no cover
            raise AssertionError("ID token is not set.")

        return self._id_token

    @property
    def expires_at(self) -> datetime:
        if self._expires_at is None:  # pragma: no cover
            raise AssertionError("Expiration time is not set.")

        return self._expires_at

    async def get_id_token(self) -> str:
        """
        Get current ID token (auto-refreshes if needed).
        """
        if self._needs_refresh():
            async with self._refresh_lock:
                # Double-check after acquiring lock
                if self._needs_refresh():
                    await self._do_refresh()

        assert self._id_token is not None
        return self._id_token

    async def refresh(self) -> TokenData:
        """
        Manually refresh ID token.
        """
        async with self._refresh_lock:
            return await self._do_refresh()

    def _needs_refresh(self) -> bool:
        if self._id_token is None or self._expires_at is None:
            return True

        now = datetime.now(timezone.utc)
        refresh_threshold = self._expires_at - timedelta(
            seconds=self._refresh_buffer_seconds
        )

        return now >= refresh_threshold

    async def _do_refresh(self) -> TokenData:
        token_data = await refresh_id_token(self.refresh_token, self.api_key)

        self.refresh_token = token_data.refresh_token
        self._id_token = token_data.id_token
        self._expires_at = token_data.expires_at

        return token_data
