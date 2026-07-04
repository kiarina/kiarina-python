import pytest

from kiarina.lib.firebase_rtdb import get_data


async def test_unauthorized(database_url: str, id_token: str) -> None:
    with pytest.raises(Exception, match="401"):
        await get_data(database_url, "/posts/other_user", id_token)


async def test_happy_path(database_url: str, user_id: str, id_token: str) -> None:
    data = await get_data(database_url, f"/posts/{user_id}", id_token)
    assert isinstance(data, dict)
    assert data.get("content") == "hello"
