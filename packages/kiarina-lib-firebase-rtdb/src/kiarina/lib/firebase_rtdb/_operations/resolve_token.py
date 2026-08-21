from kiarina.lib.firebase import Token

from .resolve_token_manager import resolve_token_manager


async def resolve_token(token: Token | None = None) -> Token:
    if token is not None:
        return token

    return await resolve_token_manager().get_token()
