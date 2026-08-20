from .resolve_token_manager import resolve_token_manager


async def resolve_id_token(id_token: str | None = None) -> str:
    if id_token is not None:
        return id_token

    return await resolve_token_manager().get_id_token()
