from .._operations.resolve_token_store import resolve_token_store
from .._schemas.token import Token
from .._services.token_manager import TokenManager
from .._settings import settings_manager
from .._types.token_store import TokenStore


def create_token_manager(
    firebase_settings_key: str | None = None,
    *,
    token_store: TokenStore | Token | None = None,
    refresh_buffer_seconds: int = 300,
) -> TokenManager:
    settings = settings_manager.get_settings(firebase_settings_key)

    return TokenManager(
        api_key=settings.api_key.get_secret_value(),
        token_store=resolve_token_store(token_store, settings),
        refresh_buffer_seconds=refresh_buffer_seconds,
    )
