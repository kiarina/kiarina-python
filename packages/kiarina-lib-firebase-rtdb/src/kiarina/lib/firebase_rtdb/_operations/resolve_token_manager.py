from kiarina.lib.firebase import TokenManager, token_manager_registry

from .._settings import settings_manager


def resolve_token_manager(token_manager: TokenManager | None = None) -> TokenManager:
    if token_manager is not None:
        return token_manager

    token_manager_name = settings_manager.get_settings().firebase_token_manager_name

    if token_manager_name is None:
        raise ValueError(
            "No token is provided and 'firebase_token_manager_name' is not configured."
        )

    return token_manager_registry.get(token_manager_name)
