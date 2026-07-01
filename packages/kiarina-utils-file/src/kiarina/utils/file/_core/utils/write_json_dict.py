import json
import os
from collections.abc import Awaitable
from typing import Any, Literal, overload

from .write_text import write_text


@overload
def write_json_dict(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    json_dict: dict[str, Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None: ...


@overload
def write_json_dict(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    json_dict: dict[str, Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> Awaitable[None]: ...


def write_json_dict(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    json_dict: dict[str, Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None | Awaitable[None]:
    json_text = json.dumps(
        json_dict, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys
    )

    def _sync() -> None:
        write_text("sync", file_path, json_text)

    def _async() -> Awaitable[None]:
        return write_text("async", file_path, json_text)

    if mode == "sync":
        _sync()
        return None
    else:
        return _async()
