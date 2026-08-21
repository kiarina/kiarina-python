from kiarina.lib.firebase import Token, token_manager_registry

from .._settings import settings_manager


async def resolve_token(token: Token | None = None) -> Token:
    if token is not None:
        return token

    token_manager = token_manager_registry.get(
        settings_manager.get_settings().firebase_settings_key
    )

    return await token_manager.get_token()
