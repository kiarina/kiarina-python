from .._schemas.token_data import TokenData
from .._types.token_store import TokenStore


class InMemoryTokenStore(TokenStore):
    def __init__(self, token_data: TokenData) -> None:
        self._token_data: TokenData = token_data

    async def get(self) -> TokenData:
        return self._token_data

    async def set(self, token_data: TokenData) -> None:
        self._token_data = token_data
