from typing import Protocol

from .._schemas.token_data import TokenData


class TokenStore(Protocol):
    """Persistent storage interface for Firebase authentication tokens."""

    async def get(self) -> TokenData: ...

    async def set(self, token_data: TokenData) -> None: ...
