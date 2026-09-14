import copy
import logging
from collections.abc import Callable, Mapping
from typing import Any, Literal, cast

logger = logging.getLogger(__name__)


class RTDBMirror:
    """
    A local copy of one Firebase Realtime Database path.

    `watch_data` binds it to the watched path and keeps it in sync with the stream.
    `update_data` applies an update to it before sending, and rolls it back if the update
    fails, so the caller reads its own write without waiting for the stream to echo it back.
    """

    def __init__(self) -> None:
        self._path: list[str] | None = None
        # Firebase sends the whole path as a put at "/" on every connect.
        self._synced = False
        self._value: Any = None

    @property
    def value(self) -> Any:
        return copy.deepcopy(self._value)

    def _bind(self, path: str) -> None:
        parts = _split_path(path)

        if self._path is not None and self._path != parts:
            raise ValueError(
                f"RTDBMirror is bound to /{'/'.join(self._path)}, not {path}"
            )

        self._path = parts

    def _apply(self, event_type: Literal["put", "patch"], path: str, data: Any) -> bool:
        """Apply a stream event and return whether the value changed."""
        parts = _split_path(path)

        if event_type == "put":
            if not parts:
                value = _normalize(copy.deepcopy(data))
                changed = not self._synced or value != self._value
                self._value = value
                self._synced = True
                return changed

            self._value, changed = _set(self._value, parts, data)
            return changed

        if not isinstance(data, Mapping):
            logger.warning(f"Patch data is not a mapping: {data!r}")
            return False

        return self._patch(parts, data)

    def _apply_update(self, path: str, values: Mapping[str, Any]) -> Callable[[], None]:
        """Apply an update and return a function that rolls it back."""
        previous: list[tuple[list[str], Any]] = []

        # Before the first snapshot there is nothing to update; the snapshot replaces it.
        if self._path is None or not self._synced:
            return lambda: None

        base = _split_path(path)

        for key, value in values.items():
            parts = base + _split_path(key)

            # Only the part of the update under the mirrored path is applied.
            if parts[: len(self._path)] != self._path:
                continue

            relative = parts[len(self._path) :]
            previous.append((relative, _get(self._value, relative)))
            self._value, _ = _set(self._value, relative, value)

        def _rollback() -> None:
            for relative, old in reversed(previous):
                self._value, _ = _set(self._value, relative, old)

        return _rollback

    def _patch(self, parts: list[str], data: Mapping[str, Any]) -> bool:
        changed = False

        # Each patch key is a path relative to the event path.
        for key, value in data.items():
            self._value, key_changed = _set(
                self._value, parts + _split_path(key), value
            )
            changed = changed or key_changed

        return changed


def _split_path(path: str) -> list[str]:
    return [part for part in path.split("/") if part]


def _get(node: Any, parts: list[str]) -> Any:
    for part in parts:
        if not isinstance(node, (dict, list)):
            return None

        node = _as_dict(node).get(part)

    return copy.deepcopy(node)


def _set(node: Any, parts: list[str], data: Any) -> tuple[Any, bool]:
    if not parts:
        value = _normalize(copy.deepcopy(data))
        return value, value != node

    # Writing a child turns a leaf into an object, as in Firebase.
    children = _as_dict(node)
    key, rest = parts[0], parts[1:]
    child, changed = _set(children.get(key), rest, data)

    if child is None:
        children.pop(key, None)
    else:
        children[key] = child

    # Firebase does not store empty objects, so an object without children is gone.
    result = children or None

    if children is not node:
        changed = result != node

    return result, changed


def _as_dict(node: Any) -> dict[str, Any]:
    if isinstance(node, dict):
        return cast(dict[str, Any], node)

    # Firebase returns objects with sequential integer keys as arrays.
    if isinstance(node, list):
        return {str(i): v for i, v in enumerate(node) if v is not None}

    return {}


def _normalize(data: Any) -> Any:
    if isinstance(data, dict):
        children = {
            k: v
            for k, v in ((k, _normalize(v)) for k, v in data.items())
            if v is not None
        }
        return children or None

    return data
