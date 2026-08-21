from .._schemas.token import Token
from .._types.token_store import TokenStore


class InMemoryTokenStore(TokenStore):
    def __init__(self, token: Token) -> None:
        self._token: Token = token

    async def get(self) -> Token:
        return self._token

    async def set(self, token: Token) -> None:
        self._token = token
