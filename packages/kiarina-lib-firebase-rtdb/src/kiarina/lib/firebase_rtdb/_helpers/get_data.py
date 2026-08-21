from typing import Any

import httpx

from kiarina.lib.firebase import Token

from .._operations.resolve_token import resolve_token
from .._schemas.rtdb_query import RTDBQuery


async def get_data(
    database_url: str,
    path: str,
    *,
    query: RTDBQuery | None = None,
    token: Token | None = None,
) -> Any:
    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": (await resolve_token(token)).id_token}

    if query is not None:
        params.update(query.to_params())

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
