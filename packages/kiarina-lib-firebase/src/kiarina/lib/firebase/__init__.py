import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._exceptions.firebase_api_error import FirebaseAPIError
    from ._exceptions.firebase_auth_error import FirebaseAuthError
    from ._exceptions.invalid_custom_token_error import InvalidCustomTokenError
    from ._exceptions.invalid_refresh_token_error import InvalidRefreshTokenError
    from ._helpers.create_token_manager import create_token_manager
    from ._helpers.exchange_custom_token import exchange_custom_token
    from ._helpers.refresh_id_token import refresh_id_token
    from ._instances.token_manager_registry import token_manager_registry
    from ._schemas.token import Token
    from ._services.file_token_store import FileTokenStore
    from ._services.in_memory_token_store import InMemoryTokenStore
    from ._services.token_manager import TokenManager
    from ._settings import FirebaseSettings, settings_manager
    from ._types.token_store import TokenStore

__all__ = [
    # ._exceptions
    "FirebaseAPIError",
    "FirebaseAuthError",
    "InvalidCustomTokenError",
    "InvalidRefreshTokenError",
    # ._helpers
    "create_token_manager",
    "exchange_custom_token",
    "refresh_id_token",
    # ._instances
    "token_manager_registry",
    # ._schemas
    "Token",
    # ._services
    "FileTokenStore",
    "InMemoryTokenStore",
    "TokenManager",
    # ._settings
    "FirebaseSettings",
    "settings_manager",
    # ._types
    "TokenStore",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._exceptions
        "FirebaseAPIError": "._exceptions.firebase_api_error",
        "FirebaseAuthError": "._exceptions.firebase_auth_error",
        "InvalidCustomTokenError": "._exceptions.invalid_custom_token_error",
        "InvalidRefreshTokenError": "._exceptions.invalid_refresh_token_error",
        # ._helpers
        "create_token_manager": "._helpers.create_token_manager",
        "exchange_custom_token": "._helpers.exchange_custom_token",
        "refresh_id_token": "._helpers.refresh_id_token",
        # ._instances
        "token_manager_registry": "._instances.token_manager_registry",
        # ._schemas
        "Token": "._schemas.token",
        # ._services
        "FileTokenStore": "._services.file_token_store",
        "InMemoryTokenStore": "._services.in_memory_token_store",
        "TokenManager": "._services.token_manager",
        # ._settings
        "FirebaseSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "TokenStore": "._types.token_store",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
