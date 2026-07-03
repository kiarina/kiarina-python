from typing import Any

import pytest

from kiarina.lib.firebase_rtdb import get_data


async def test_unauthorized(database_url: Any, id_token: Any) -> None:
    with pytest.raises(Exception, match="401"):
        await get_data(database_url, "/posts/other_user", id_token)


async def test_happy_path(database_url: Any, user_id: Any, id_token: Any) -> None:
    data = await get_data(database_url, f"/posts/{user_id}", id_token)
    assert isinstance(data, dict)
    assert data.get("content") == "hello"
