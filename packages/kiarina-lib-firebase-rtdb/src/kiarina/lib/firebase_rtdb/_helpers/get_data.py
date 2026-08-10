from typing import Any

import httpx


async def get_data(
    database_url: str,
    path: str,
    id_token: str,
) -> Any:
    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": id_token}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
