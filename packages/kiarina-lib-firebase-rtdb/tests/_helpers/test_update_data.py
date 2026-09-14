import base64
import json
from typing import Any

import httpx
import pytest

from kiarina.lib.firebase import Token
from kiarina.lib.firebase_rtdb import RTDBMirror, update_data
from kiarina.lib.firebase_rtdb._helpers import update_data as update_data_module


def make_token(id_token: str = "id-token") -> Token:
    payload = {"exp": 4102444800, "sub": "user_1", "aud": "project_1"}
    segment = (
        base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    return Token(refresh_token="refresh-token", id_token=f"header.{segment}.signature")


class _FakeResponse:
    is_success = True

    def __init__(self, payload: Any) -> None:
        self._payload = payload

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
    fake_token = make_token()

    result = await update_data(
        "https://example-rtdb.firebaseio.com/",
        "/users/u1/chats/c1/entries",
        {"01A/read": True, "01B/read": True},
        token=fake_token,
    )

    assert result == {"read": True}
    assert calls == [
        {
            "url": "https://example-rtdb.firebaseio.com/users/u1/chats/c1/entries.json",
            "params": {"auth": fake_token.id_token},
            "json": {"01A/read": True, "01B/read": True},
        }
    ]


async def test_none_values_are_kept_for_deletion(calls: list[dict[str, Any]]) -> None:
    fake_token = make_token()

    await update_data(
        "https://example-rtdb.firebaseio.com",
        "/users/u1/chats/c1/entries",
        {"01A": None},
        token=fake_token,
    )

    assert calls[0]["json"] == {"01A": None}


async def test_applies_the_update_to_the_mirror(calls: list[dict[str, Any]]) -> None:
    mirror = RTDBMirror()
    mirror._bind("/users/u1/chats/c1/entries")
    mirror._apply("put", "/", {"01A": {"read": False}, "01B": {"read": False}})

    await update_data(
        "https://example-rtdb.firebaseio.com",
        "/users/u1/chats/c1/entries",
        {"01A/read": True},
        token=make_token(),
        mirror=mirror,
    )

    assert mirror.value == {"01A": {"read": True}, "01B": {"read": False}}


async def test_failed_update_leaves_the_mirror(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FailingResponse(_FakeResponse):
        is_success = False

    class _FailingClient(_FakeClient):
        async def patch(self, url: str, **kwargs: Any) -> _FakeResponse:
            return _FailingResponse(None)

    async def _raise(response: Any, *, operation: str) -> None:
        raise RuntimeError("update failed")

    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: _FailingClient([], None))
    monkeypatch.setattr(update_data_module, "raise_for_status", _raise)
    mirror = RTDBMirror()
    mirror._bind("/p")
    mirror._apply("put", "/", {"a": 1})

    with pytest.raises(RuntimeError, match="update failed"):
        await update_data(
            "https://example-rtdb.firebaseio.com",
            "/p",
            {"a": 2},
            token=make_token(),
            mirror=mirror,
        )

    assert mirror.value == {"a": 1}
