from collections.abc import AsyncIterator
from typing import Any, cast

import pytest

from kiarina.lib.firebase import TokenManager
from kiarina.lib.firebase_rtdb import RTDBMirror
from kiarina.lib.firebase_rtdb._helpers import watch_data as watch_data_module

_StreamEvent = watch_data_module._StreamEvent


def _put(path: str, data: Any) -> Any:
    return _StreamEvent(event_type="put", path=path, data=data)


def _patch(path: str, data: Any) -> Any:
    return _StreamEvent(event_type="patch", path=path, data=data)


def _install_events(monkeypatch: pytest.MonkeyPatch, events: list[Any]) -> None:
    async def _fake_watch_events(*args: Any) -> AsyncIterator[Any]:
        for event in events:
            if callable(event):
                await event()
            else:
                yield event

    monkeypatch.setattr(watch_data_module, "_watch_events", _fake_watch_events)


def _watch(mirror: RTDBMirror | None = None) -> AsyncIterator[Any]:
    return watch_data_module.watch_data(
        "https://db.example.com",
        "/p",
        token_manager=cast(TokenManager, object()),
        mirror=mirror,
    )


async def _collect(mirror: RTDBMirror | None = None) -> list[Any]:
    return [value async for value in _watch(mirror)]


async def test_yields_nothing_before_the_first_root_put(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_events(monkeypatch, [_put("/a", 1), _put("/", {"b": 2}), _put("/c", 3)])

    assert await _collect() == [{"b": 2}, {"b": 2, "c": 3}]


async def test_yields_none_when_the_node_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_events(monkeypatch, [_put("/", None), _put("/a", 1), _put("/a", None)])

    assert await _collect() == [None, {"a": 1}, None]


async def test_skips_unchanged_values(monkeypatch: pytest.MonkeyPatch) -> None:
    # A reconnect sends the same root put again.
    _install_events(
        monkeypatch,
        [
            _put("/", {"a": 1}),
            _put("/", {"a": 1}),
            _patch("/", {"a": 1}),
            _put("/a", 2),
        ],
    )

    assert await _collect() == [{"a": 1}, {"a": 2}]


async def test_yielded_values_are_independent_copies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_events(monkeypatch, [_put("/", {"a": {"x": 1}}), _put("/a/y", 2)])

    values = []

    async for value in _watch():
        values.append(value)
        value["a"]["x"] = 100

    assert values == [{"a": {"x": 100}}, {"a": {"x": 100, "y": 2}}]


async def test_keeps_the_given_mirror_in_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_events(monkeypatch, [_put("/", {"a": 1}), _put("/b", 2)])
    mirror = RTDBMirror()

    await _collect(mirror)

    assert mirror.value == {"a": 1, "b": 2}


async def test_own_update_is_not_yielded_again(monkeypatch: pytest.MonkeyPatch) -> None:
    mirror = RTDBMirror()

    async def _update() -> None:
        # What update_data does after the write succeeds.
        mirror._apply_update("/p", {"01A/read": True})

    _install_events(
        monkeypatch,
        [
            _put("/", {"01A": {"read": False}}),
            _update,
            # The stream echoes the write back.
            _put("/01A/read", True),
            _put("/01B", {"read": False}),
        ],
    )

    assert await _collect(mirror) == [
        {"01A": {"read": False}},
        {"01A": {"read": True}, "01B": {"read": False}},
    ]


async def test_rejects_a_mirror_bound_to_another_path() -> None:
    mirror = RTDBMirror()
    mirror._bind("/q")

    with pytest.raises(ValueError, match="bound to /q"):
        await _collect(mirror)
