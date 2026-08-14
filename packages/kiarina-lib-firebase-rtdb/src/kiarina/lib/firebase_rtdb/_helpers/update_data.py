from collections.abc import Mapping
from typing import Any

import httpx


async def update_data(
    database_url: str,
    path: str,
    id_token: str,
    values: Mapping[str, Any],
) -> Any:
    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": id_token}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.patch(url, params=params, json=dict(values))
        response.raise_for_status()
        return response.json()
