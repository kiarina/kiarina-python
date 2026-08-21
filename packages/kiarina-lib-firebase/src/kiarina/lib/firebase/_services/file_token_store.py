from kiarina.utils.file.asyncio import read_json_dict, write_json_dict

from .._schemas.token import Token
from .._types.token_store import TokenStore


class FileTokenStore(TokenStore):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    async def get(self) -> Token:
        data = await read_json_dict(self.file_path)

        if not data:
            raise FileNotFoundError(f"Token file not found: {self.file_path}")

        return Token.model_validate(data)

    async def set(self, token: Token) -> None:
        await write_json_dict(self.file_path, token.model_dump(mode="json"))
