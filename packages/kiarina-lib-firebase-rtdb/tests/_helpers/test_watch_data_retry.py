import logging
from collections.abc import AsyncIterator, Iterator
from typing import Any, cast

import httpx
import pytest

from kiarina.lib.firebase import (
    FirebaseAPIError,
    InvalidRefreshTokenError,
    Token,
    TokenManager,
)
from kiarina.lib.firebase_rtdb import DataChangeEvent, settings_manager
from kiarina.lib.firebase_rtdb._helpers import watch_data as watch_data_module

_TOKEN = Token(
    refresh_token="refresh-token",
    id_token="header.eyJleHAiOiA0MTAyNDQ0ODAwfQ.signature",
)

watch_data = watch_data_module.watch_data

_AuthRevokedError = watch_data_module._AuthRevokedError

# A scripted stream connection: events to emit, then an optional error to raise.
_Connection = tuple[list[DataChangeEvent], Exception | None]


@pytest.fixture(autouse=True)
def no_retry_delay() -> Iterator[None]:
    settings_manager.user_config = {
        "initial_retry_delay": 0.0,
        "max_retry_delay": 0.0,
    }
    yield
    settings_manager.user_config = {}


class _FakeTokenManager:
    def __init__(self, refresh_errors: list[Exception | None] | None = None) -> None:
        self.refresh_errors = refresh_errors or []
        self.refresh_count = 0

    async def get_token(self) -> Any:
        return _TOKEN

    async def refresh(self) -> Any:
        self.refresh_count += 1

        if self.refresh_errors:
            error = self.refresh_errors.pop(0)

            if error is not None:
                raise error

        return None


def _fake_token_manager(
    refresh_errors: list[Exception | None] | None = None,
) -> tuple[TokenManager, _FakeTokenManager]:
    fake = _FakeTokenManager(refresh_errors)
    return cast(TokenManager, fake), fake


def _install_stream(
    monkeypatch: pytest.MonkeyPatch, connections: list[_Connection]
) -> list[int]:
    """Replace the network stream with a script, returning the refresh count per connect."""
    refresh_counts: list[int] = []
    remaining = list(connections)

    async def _fake_watch_stream(
        database_url: str,
        path: str,
        token_manager: Any,
        stop_event: Any = None,
    ) -> AsyncIterator[DataChangeEvent]:
        refresh_counts.append(token_manager.refresh_count)

        if not remaining:
            raise AssertionError("Stream reconnected more times than scripted")

        events, error = remaining.pop(0)

        for event in events:
            yield event

        if error is not None:
            raise error

    monkeypatch.setattr(watch_data_module, "_watch_stream", _fake_watch_stream)
    return refresh_counts


def _event(data: str) -> DataChangeEvent:
    return DataChangeEvent(event_type="put", path="/", data=data)


async def _collect(token_manager: TokenManager) -> list[DataChangeEvent]:
    return [
        event
        async for event in watch_data(
            "https://db.example.com", "/p", token_manager=token_manager
        )
    ]


async def test_auth_revoked_refreshes_and_reconnects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token_manager, fake = _fake_token_manager()
    refresh_counts = _install_stream(
        monkeypatch,
        [
            ([_event("first")], _AuthRevokedError()),
            ([_event("second")], None),
        ],
    )

    events = await _collect(token_manager)

    assert [event.data for event in events] == ["first", "second"]
    assert fake.refresh_count == 1
    # The reconnect happens only after the refresh.
    assert refresh_counts == [0, 1]


async def test_refresh_failure_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    token_manager, fake = _fake_token_manager(
        [FirebaseAPIError("Request failed: connection reset")]
    )
    _install_stream(
        monkeypatch,
        [
            ([_event("first")], _AuthRevokedError()),
            ([_event("second")], None),
        ],
    )

    events = await _collect(token_manager)

    assert [event.data for event in events] == ["first", "second"]
    assert fake.refresh_count == 2


async def test_invalid_refresh_token_stops_the_watch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token_manager, _ = _fake_token_manager([InvalidRefreshTokenError("revoked")])
    _install_stream(monkeypatch, [([_event("first")], _AuthRevokedError())])

    with pytest.raises(InvalidRefreshTokenError):
        await _collect(token_manager)


async def test_non_retryable_api_error_stops_the_watch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token_manager, _ = _fake_token_manager(
        [FirebaseAPIError("Bad request", status_code=400)]
    )
    _install_stream(monkeypatch, [([_event("first")], _AuthRevokedError())])

    with pytest.raises(FirebaseAPIError):
        await _collect(token_manager)


async def test_network_error_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    token_manager, fake = _fake_token_manager()
    _install_stream(
        monkeypatch,
        [
            ([], httpx.ConnectError("connection refused")),
            ([_event("first")], None),
        ],
    )

    events = await _collect(token_manager)

    assert [event.data for event in events] == ["first"]
    assert fake.refresh_count == 0


async def test_auth_revoked_without_events_backs_off(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    token_manager, _ = _fake_token_manager()
    _install_stream(
        monkeypatch,
        [
            ([], _AuthRevokedError()),
            ([_event("first")], None),
        ],
    )

    with caplog.at_level(logging.WARNING, logger="kiarina.lib.firebase_rtdb"):
        events = await _collect(token_manager)

    assert [event.data for event in events] == ["first"]
    assert any(
        "Auth revoked before any event" in record.message for record in caplog.records
    )
