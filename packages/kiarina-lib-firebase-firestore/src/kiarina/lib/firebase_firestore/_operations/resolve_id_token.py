from kiarina.lib.firebase import token_manager_registry

from .._settings import settings_manager


async def resolve_id_token(id_token: str | None = None) -> str:
    if id_token is not None:
        return id_token

    token_manager = token_manager_registry.get(
        settings_manager.get_settings().firebase_settings_key
    )

    return await token_manager.get_id_token()
