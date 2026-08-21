from .._schemas.token import Token
from .._services.file_token_store import FileTokenStore
from .._services.in_memory_token_store import InMemoryTokenStore
from .._settings import FirebaseSettings
from .._types.token_store import TokenStore


def resolve_token_store(
    token_store: TokenStore | Token | None,
    settings: FirebaseSettings,
) -> TokenStore:
    if isinstance(token_store, Token):
        return InMemoryTokenStore(token_store)

    if token_store is not None:
        return token_store

    if settings.token_file_path is not None:
        return FileTokenStore(settings.token_file_path)

    raise ValueError(
        "'token_store' is required when 'token_file_path' is not configured."
    )
