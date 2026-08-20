from kiarina.lib.firebase import token_manager_registry

from .._settings import settings_manager


async def resolve_id_token(id_token: str | None = None) -> str:
    if id_token is not None:
        return id_token

    token_manager_name = settings_manager.get_settings().firebase_token_manager_name

    if token_manager_name is None:
        raise ValueError(
            "No token is provided and 'firebase_token_manager_name' is not configured."
        )

    return await token_manager_registry.get(token_manager_name).get_id_token()
