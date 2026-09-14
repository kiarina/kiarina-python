import gzip
import logging
import traceback
from collections.abc import Iterator
from typing import Any, cast

import httpx
import pytest

from kiarina.lib.firebase import Token, TokenManager
from kiarina.lib.firebase_rtdb import (
    get_data,
    settings_manager,
    update_data,
    watch_data,
)
from kiarina.lib.firebase_rtdb._helpers import watch_data as watch_data_module

_SIGNATURE = "secret-signature"
_ID_TOKEN = f"header.eyJleHAiOiA0MTAyNDQ0ODAwfQ.{_SIGNATURE}"
_TOKEN = Token(refresh_token="refresh-token", id_token=_ID_TOKEN)
_DATABASE_URL = "https://example-rtdb.firebaseio.com"
_PATH = "/users/u1/state"
_STATUSES = [401, 403, 503]

_RealAsyncClient = httpx.AsyncClient


@pytest.fixture(autouse=True)
def no_retry_delay() -> Iterator[None]:
    settings_manager.user_config = {
        "initial_retry_delay": 0.0,
        "max_retry_delay": 0.0,
    }
    yield
    settings_manager.user_config = {}


class _FakeTokenManager:
    async def get_token(self) -> Token:
        return _TOKEN

    async def refresh(self) -> Token:  # pragma: no cover
        return _TOKEN


def _install_responses(
    monkeypatch: pytest.MonkeyPatch, responses: list[httpx.Response]
) -> list[httpx.Request]:
    sent: list[httpx.Request] = []
    remaining = list(responses)

    def _handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return remaining.pop(0)

    def _client(**kwargs: Any) -> httpx.AsyncClient:
        return _RealAsyncClient(transport=httpx.MockTransport(_handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", _client)
    return sent


def _error_response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code, json={"error": "Permission denied"})


def _assert_redacted(
    error: httpx.HTTPStatusError, status_code: int, operation: str
) -> None:
    assert error.response.status_code == status_code
    assert error.response.json() == {"error": "Permission denied"}
    assert f"RTDB {operation} failed" in str(error)
    assert f"'{status_code} " in str(error)
    assert f"{_DATABASE_URL}{_PATH}.json" in str(error)

    assert error.__cause__ is None
    assert error.__context__ is None

    texts = [
        str(error),
        repr(error),
        "".join(traceback.format_exception(error)),
        str(error.request.url),
        str(error.response.url),
        str(error.response.request.url),
        str(error.request.headers),
    ]

    for text in texts:
        assert _SIGNATURE not in text


def _assert_token_sent(sent: list[httpx.Request]) -> None:
    assert sent[0].url.params["auth"] == _ID_TOKEN


@pytest.mark.parametrize("status_code", _STATUSES)
async def test_get_data_error_omits_token(
    monkeypatch: pytest.MonkeyPatch, status_code: int
) -> None:
    sent = _install_responses(monkeypatch, [_error_response(status_code)])

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await get_data(_DATABASE_URL, _PATH, token=_TOKEN)

    _assert_token_sent(sent)
    _assert_redacted(exc_info.value, status_code, "get")


@pytest.mark.parametrize("status_code", _STATUSES)
async def test_update_data_error_omits_token(
    monkeypatch: pytest.MonkeyPatch, status_code: int
) -> None:
    sent = _install_responses(monkeypatch, [_error_response(status_code)])

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await update_data(_DATABASE_URL, _PATH, {"read": True}, token=_TOKEN)

    _assert_token_sent(sent)
    _assert_redacted(exc_info.value, status_code, "update")
    assert exc_info.value.request.method == "PATCH"


@pytest.mark.parametrize("status_code", _STATUSES)
async def test_watch_stream_error_omits_token(
    monkeypatch: pytest.MonkeyPatch, status_code: int
) -> None:
    sent = _install_responses(monkeypatch, [_error_response(status_code)])
    token_manager = cast(TokenManager, _FakeTokenManager())

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        async for _ in watch_data_module._watch_stream(
            _DATABASE_URL, _PATH, token_manager
        ):
            pass  # pragma: no cover

    _assert_token_sent(sent)
    _assert_redacted(exc_info.value, status_code, "watch")


@pytest.mark.parametrize("status_code", _STATUSES)
async def test_watch_data_retries_without_logging_token(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    status_code: int,
) -> None:
    _install_responses(
        monkeypatch,
        [
            _error_response(status_code),
            httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                content=b'event: put\ndata: {"path": "/", "data": "ok"}\n\n',
            ),
        ],
    )
    token_manager = cast(TokenManager, _FakeTokenManager())

    with caplog.at_level(logging.DEBUG, logger="kiarina.lib.firebase_rtdb"):
        values = [
            value
            async for value in watch_data(
                _DATABASE_URL, _PATH, token_manager=token_manager
            )
        ]

    assert values == ["ok"]
    assert any(str(status_code) in record.message for record in caplog.records)
    assert all(_SIGNATURE not in record.message for record in caplog.records)


async def test_compressed_error_body_is_kept_decoded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = gzip.compress(b'{"error": "Permission denied"}')
    _install_responses(
        monkeypatch,
        [httpx.Response(403, headers={"Content-Encoding": "gzip"}, content=body)],
    )

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await get_data(_DATABASE_URL, _PATH, token=_TOKEN)

    _assert_redacted(exc_info.value, 403, "get")


async def test_error_body_is_optional_for_redirect_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_responses(monkeypatch, [httpx.Response(304)])

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await get_data(_DATABASE_URL, _PATH, token=_TOKEN)

    assert exc_info.value.response.status_code == 304
    assert "Redirect response" in str(exc_info.value)
    assert _SIGNATURE not in str(exc_info.value)
