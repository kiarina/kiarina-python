from collections.abc import Mapping
from typing import Any

import httpx

from .._operations.resolve_id_token import resolve_id_token


async def update_data(
    database_url: str,
    path: str,
    values: Mapping[str, Any],
    *,
    id_token: str | None = None,
) -> Any:
    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": await resolve_id_token(id_token)}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.patch(url, params=params, json=dict(values))
        response.raise_for_status()
        return response.json()
