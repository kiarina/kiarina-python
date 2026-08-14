from typing import Any

import httpx
import pytest

from kiarina.lib.firebase_rtdb import RTDBQuery, get_data


async def test_unauthorized(database_url: str, id_token: str) -> None:
    with pytest.raises(Exception, match="401"):
        await get_data(database_url, "/posts/other_user", id_token)


async def test_happy_path(database_url: str, user_id: str, id_token: str) -> None:
    data = await get_data(database_url, f"/posts/{user_id}", id_token)
    assert isinstance(data, dict)
    assert data.get("content") == "hello"


class _FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return {}


class _FakeClient:
    def __init__(self, calls: list[dict[str, str]]) -> None:
        self.calls = calls

    async def __aenter__(self) -> "_FakeClient":
        return self

    async def __aexit__(self, *args: object) -> bool:
        return False

    async def get(
        self, url: str, *, params: dict[str, str] | None = None
    ) -> _FakeResponse:
        self.calls.append(params or {})
        return _FakeResponse()


@pytest.fixture
def sent_params(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, str]]:
    recorded: list[dict[str, str]] = []
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: _FakeClient(recorded))
    return recorded


async def test_query_is_merged_into_params(sent_params: list[dict[str, str]]) -> None:
    await get_data(
        "https://example-rtdb.firebaseio.com",
        "/users/u1/chats/c1/entries",
        "id-token",
        query=RTDBQuery(order_by="$key", start_after="01ABC", limit_to_last=5),
    )

    assert sent_params == [
        {
            "auth": "id-token",
            "orderBy": '"$key"',
            "startAfter": '"01ABC"',
            "limitToLast": "5",
        }
    ]


async def test_without_query_only_sends_auth(sent_params: list[dict[str, str]]) -> None:
    await get_data("https://example-rtdb.firebaseio.com", "/posts", "id-token")
    assert sent_params == [{"auth": "id-token"}]
