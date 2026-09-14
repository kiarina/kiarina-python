from collections.abc import Mapping
from typing import Any

import httpx

from kiarina.lib.firebase import Token

from .._models.rtdb_mirror import RTDBMirror
from .._operations.resolve_token import resolve_token
from .._utils.raise_for_status import raise_for_status


async def update_data(
    database_url: str,
    path: str,
    values: Mapping[str, Any],
    *,
    token: Token | None = None,
    mirror: RTDBMirror | None = None,
) -> Any:
    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": (await resolve_token(token)).id_token}

    # Apply before sending: the stream can echo the write back before the response arrives.
    rollback = mirror._apply_update(path, values) if mirror is not None else None

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.patch(url, params=params, json=dict(values))
            await raise_for_status(response, operation="update")

    except BaseException:
        if rollback is not None:
            rollback()

        raise

    return response.json()
