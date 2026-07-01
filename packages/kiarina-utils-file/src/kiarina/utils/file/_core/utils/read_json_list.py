import json
import os
from collections.abc import Awaitable
from typing import Any, Literal, overload

from .read_text import read_text


@overload
def read_json_list(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> list[Any] | None: ...


@overload
def read_json_list(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> Awaitable[list[Any] | None]: ...


def read_json_list(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> list[Any] | None | Awaitable[list[Any] | None]:

    def _after(raw_text: str | None) -> list[Any] | None:
        if raw_text is None:
            return default

        data = json.loads(raw_text)

        if not isinstance(data, list):
            raise json.JSONDecodeError("JSON data is not a list", raw_text, 0)

        return data

    def _sync() -> list[Any] | None:
        raw_text = read_text("sync", file_path)
        return _after(raw_text)

    async def _async() -> list[Any] | None:
        raw_text = await read_text("async", file_path)
        return _after(raw_text)

    if mode == "sync":
        return _sync()
    else:
        return _async()
