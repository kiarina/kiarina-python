from typing import Any

import httpx
import pytest

from kiarina.lib.firebase_rtdb import update_data


class _FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


class _FakeClient:
    def __init__(self, calls: list[dict[str, Any]], payload: Any) -> None:
        self.calls = calls
        self.payload = payload

    async def __aenter__(self) -> "_FakeClient":
        return self

    async def __aexit__(self, *args: object) -> bool:
        return False

    async def patch(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        json: Any = None,
    ) -> _FakeResponse:
        self.calls.append({"url": url, "params": params, "json": json})
        return _FakeResponse(self.payload)


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    recorded: list[dict[str, Any]] = []
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **_: _FakeClient(recorded, {"read": True}),
    )
    return recorded


async def test_sends_patch_with_auth(calls: list[dict[str, Any]]) -> None:
    result = await update_data(
        "https://example-rtdb.firebaseio.com/",
        "/users/u1/chats/c1/entries",
        {"01A/read": True, "01B/read": True},
        id_token="id-token",
    )

    assert result == {"read": True}
    assert calls == [
        {
            "url": "https://example-rtdb.firebaseio.com/users/u1/chats/c1/entries.json",
            "params": {"auth": "id-token"},
            "json": {"01A/read": True, "01B/read": True},
        }
    ]


async def test_none_values_are_kept_for_deletion(calls: list[dict[str, Any]]) -> None:
    await update_data(
        "https://example-rtdb.firebaseio.com",
        "/users/u1/chats/c1/entries",
        {"01A": None},
        id_token="id-token",
    )

    assert calls[0]["json"] == {"01A": None}
