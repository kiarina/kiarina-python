from collections.abc import AsyncIterator
from typing import Any, cast

import pytest

from kiarina.lib.firebase import TokenManager
from kiarina.lib.firebase_rtdb._helpers import watch_data as watch_data_module

_Snapshot = watch_data_module._Snapshot
_StreamEvent = watch_data_module._StreamEvent


def _put(path: str, data: Any) -> Any:
    return _StreamEvent(event_type="put", path=path, data=data)


def _patch(path: str, data: Any) -> Any:
    return _StreamEvent(event_type="patch", path=path, data=data)


def _apply(*events: Any) -> Any:
    snapshot = _Snapshot()

    for event in events:
        snapshot.apply(event)

    return snapshot.value


# --------------------------------------------------
# Snapshot
# --------------------------------------------------


def test_root_put_replaces_the_value() -> None:
    assert _apply(_put("/", {"a": 1}), _put("/", {"b": 2})) == {"b": 2}


def test_root_put_of_null_means_the_node_is_absent() -> None:
    assert _apply(_put("/", {"a": 1}), _put("/", None)) is None


def test_root_put_of_a_leaf() -> None:
    assert _apply(_put("/", "hello")) == "hello"


def test_child_put_sets_a_nested_value() -> None:
    assert _apply(_put("/", {"a": {"x": 1}}), _put("/a/y", 2)) == {
        "a": {"x": 1, "y": 2}
    }


def test_child_put_of_null_deletes_the_child() -> None:
    assert _apply(_put("/", {"a": 1, "b": 2}), _put("/a", None)) == {"b": 2}


def test_deleting_the_last_child_removes_empty_parents() -> None:
    assert _apply(_put("/", {"a": {"x": 1}, "b": 2}), _put("/a/x", None)) == {"b": 2}
    assert _apply(_put("/", {"a": {"x": 1}}), _put("/a/x", None)) is None


def test_child_put_under_a_leaf_turns_it_into_an_object() -> None:
    assert _apply(_put("/", "hello"), _put("/a", 1)) == {"a": 1}


def test_child_put_under_an_array_turns_it_into_an_object() -> None:
    assert _apply(_put("/", ["x", "y"]), _put("/2", "z")) == {
        "0": "x",
        "1": "y",
        "2": "z",
    }


def test_patch_merges_children() -> None:
    assert _apply(
        _put("/", {"a": {"x": 1, "y": 2}}),
        _patch("/a", {"y": 3, "z": 4}),
    ) == {"a": {"x": 1, "y": 3, "z": 4}}


def test_patch_does_not_replace_the_node() -> None:
    assert _apply(_put("/", {"a": 1, "b": 2}), _patch("/", {"b": 3})) == {
        "a": 1,
        "b": 3,
    }


def test_patch_null_deletes_the_child() -> None:
    assert _apply(_put("/", {"a": 1, "b": 2}), _patch("/", {"a": None})) == {"b": 2}


def test_patch_keys_are_paths() -> None:
    assert _apply(
        _put("/", {"a": {"x": 1}}),
        _patch("/", {"a/y": 2, "b/c": 3}),
    ) == {"a": {"x": 1, "y": 2}, "b": {"c": 3}}


def test_put_drops_empty_objects_and_nulls() -> None:
    assert _apply(_put("/", {"a": {}, "b": None, "c": {"d": None}, "e": 1})) == {"e": 1}


def test_synced_after_the_first_root_put() -> None:
    snapshot = _Snapshot()
    snapshot.apply(_put("/a", 1))
    assert snapshot.synced is False

    snapshot.apply(_put("/", None))
    assert snapshot.synced is True


# --------------------------------------------------
# watch_data
# --------------------------------------------------


def _install_events(monkeypatch: pytest.MonkeyPatch, events: list[Any]) -> None:
    async def _fake_watch_events(*args: Any) -> AsyncIterator[Any]:
        for event in events:
            yield event

    monkeypatch.setattr(watch_data_module, "_watch_events", _fake_watch_events)


async def _collect() -> list[Any]:
    return [
        value
        async for value in watch_data_module.watch_data(
            "https://db.example.com",
            "/p",
            token_manager=cast(TokenManager, object()),
        )
    ]


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

    async for value in watch_data_module.watch_data(
        "https://db.example.com",
        "/p",
        token_manager=cast(TokenManager, object()),
    ):
        values.append(value)
        value["a"]["x"] = 100

    assert values == [{"a": {"x": 100}}, {"a": {"x": 100, "y": 2}}]
