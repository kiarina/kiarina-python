from typing import Any

import pytest

from kiarina.lib.firebase_rtdb import RTDBMirror


def _apply(*events: tuple[Any, str, Any]) -> Any:
    mirror = RTDBMirror()

    for event_type, path, data in events:
        mirror._apply(event_type, path, data)

    return mirror.value


def _synced(value: Any, path: str = "/p") -> RTDBMirror:
    mirror = RTDBMirror()
    mirror._bind(path)
    mirror._apply("put", "/", value)
    return mirror


# --------------------------------------------------
# Stream events
# --------------------------------------------------


def test_root_put_replaces_the_value() -> None:
    assert _apply(("put", "/", {"a": 1}), ("put", "/", {"b": 2})) == {"b": 2}


def test_root_put_of_null_means_the_node_is_absent() -> None:
    assert _apply(("put", "/", {"a": 1}), ("put", "/", None)) is None


def test_root_put_of_a_leaf() -> None:
    assert _apply(("put", "/", "hello")) == "hello"


def test_child_put_sets_a_nested_value() -> None:
    assert _apply(("put", "/", {"a": {"x": 1}}), ("put", "/a/y", 2)) == {
        "a": {"x": 1, "y": 2}
    }


def test_child_put_of_null_deletes_the_child() -> None:
    assert _apply(("put", "/", {"a": 1, "b": 2}), ("put", "/a", None)) == {"b": 2}


def test_deleting_the_last_child_removes_empty_parents() -> None:
    assert _apply(("put", "/", {"a": {"x": 1}, "b": 2}), ("put", "/a/x", None)) == {
        "b": 2
    }
    assert _apply(("put", "/", {"a": {"x": 1}}), ("put", "/a/x", None)) is None


def test_child_put_under_a_leaf_turns_it_into_an_object() -> None:
    assert _apply(("put", "/", "hello"), ("put", "/a", 1)) == {"a": 1}


def test_child_put_under_an_array_turns_it_into_an_object() -> None:
    assert _apply(("put", "/", ["x", "y"]), ("put", "/2", "z")) == {
        "0": "x",
        "1": "y",
        "2": "z",
    }


def test_patch_merges_children() -> None:
    assert _apply(
        ("put", "/", {"a": {"x": 1, "y": 2}}),
        ("patch", "/a", {"y": 3, "z": 4}),
    ) == {"a": {"x": 1, "y": 3, "z": 4}}


def test_patch_null_deletes_the_child() -> None:
    assert _apply(("put", "/", {"a": 1, "b": 2}), ("patch", "/", {"a": None})) == {
        "b": 2
    }


def test_patch_keys_are_paths() -> None:
    assert _apply(
        ("put", "/", {"a": {"x": 1}}),
        ("patch", "/", {"a/y": 2, "b/c": 3}),
    ) == {"a": {"x": 1, "y": 2}, "b": {"c": 3}}


def test_put_drops_empty_objects_and_nulls() -> None:
    assert _apply(("put", "/", {"a": {}, "b": None, "c": {"d": None}, "e": 1})) == {
        "e": 1
    }


def test_apply_reports_whether_the_value_changed() -> None:
    mirror = RTDBMirror()

    assert mirror._apply("put", "/", None) is True
    assert mirror._apply("put", "/", None) is False
    assert mirror._apply("put", "/a", 1) is True
    assert mirror._apply("patch", "/", {"a": 1}) is False
    assert mirror._apply("put", "/b", None) is False
    assert mirror._apply("patch", "/", {"a": None}) is True


def test_value_is_an_independent_copy() -> None:
    mirror = _synced({"a": {"x": 1}})

    mirror.value["a"]["x"] = 100

    assert mirror.value == {"a": {"x": 1}}


# --------------------------------------------------
# Binding
# --------------------------------------------------


def test_binding_to_another_path_is_rejected() -> None:
    mirror = RTDBMirror()
    mirror._bind("/p")
    mirror._bind("/p/")

    with pytest.raises(ValueError, match="bound to /p"):
        mirror._bind("/q")


# --------------------------------------------------
# Updates
# --------------------------------------------------


def test_update_at_the_mirrored_path() -> None:
    mirror = _synced({"01A": {"read": False}, "01B": {"read": False}})

    mirror._apply_update("/p", {"01A/read": True, "01B": None})

    assert mirror.value == {"01A": {"read": True}}


def test_update_below_the_mirrored_path() -> None:
    mirror = _synced({"01A": {"read": False}})

    mirror._apply_update("/p/01A", {"read": True})

    assert mirror.value == {"01A": {"read": True}}


def test_update_above_the_mirrored_path_applies_only_the_part_under_it() -> None:
    mirror = _synced({"01A": {"read": False}})

    mirror._apply_update("/", {"p/01A/read": True, "q/01A/read": True})

    assert mirror.value == {"01A": {"read": True}}


def test_update_outside_the_mirrored_path_is_ignored() -> None:
    mirror = _synced({"a": 1})

    mirror._apply_update("/q", {"a": 2})

    assert mirror.value == {"a": 1}


def test_update_before_the_first_snapshot_is_ignored() -> None:
    mirror = RTDBMirror()
    mirror._bind("/p")

    mirror._apply_update("/p", {"a": 1})
    assert mirror.value is None

    mirror._apply("put", "/", {"b": 2})
    assert mirror.value == {"b": 2}


def test_update_on_an_unbound_mirror_is_ignored() -> None:
    mirror = RTDBMirror()

    mirror._apply_update("/p", {"a": 1})

    assert mirror.value is None


def test_rollback_restores_what_the_update_changed() -> None:
    mirror = _synced({"a": {"x": 1}, "b": 2})

    rollback = mirror._apply_update("/p", {"a/x": 10, "a/y": 20, "b": None, "c": 3})
    assert mirror.value == {"a": {"x": 10, "y": 20}, "c": 3}

    rollback()
    assert mirror.value == {"a": {"x": 1}, "b": 2}


def test_rollback_restores_overlapping_keys_in_reverse() -> None:
    mirror = _synced({"a": {"x": 1}})

    rollback = mirror._apply_update("/p", {"a": {"y": 2}, "a/z": 3})
    assert mirror.value == {"a": {"y": 2, "z": 3}}

    rollback()
    assert mirror.value == {"a": {"x": 1}}


def test_rollback_keeps_stream_changes_to_other_paths() -> None:
    mirror = _synced({"a": 1})

    rollback = mirror._apply_update("/p", {"a": 2})
    mirror._apply("put", "/b", 3)
    rollback()

    assert mirror.value == {"a": 1, "b": 3}
