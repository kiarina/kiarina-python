from typing import Protocol

from .._schemas.token import Token


class TokenStore(Protocol):
    """Persistent storage interface for Firebase authentication tokens."""

    async def get(self) -> Token: ...

    async def set(self, token: Token) -> None: ...
