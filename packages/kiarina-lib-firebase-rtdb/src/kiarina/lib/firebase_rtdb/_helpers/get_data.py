from typing import Any

import httpx

from .._operations.resolve_id_token import resolve_id_token
from .._schemas.rtdb_query import RTDBQuery


async def get_data(
    database_url: str,
    path: str,
    *,
    query: RTDBQuery | None = None,
    id_token: str | None = None,
) -> Any:
    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": await resolve_id_token(id_token)}

    if query is not None:
        params.update(query.to_params())

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
