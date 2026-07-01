import os
from collections.abc import Awaitable
from typing import Literal, overload

from .write_binary import write_binary


@overload
def write_text(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    raw_text: str,
) -> None: ...


@overload
def write_text(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    raw_text: str,
) -> Awaitable[None]: ...


def write_text(
    mode: Literal["sync", "async"], file_path: str | os.PathLike[str], raw_text: str
) -> None | Awaitable[None]:
    raw_data = raw_text.encode("utf-8", errors="replace")

    def _sync() -> None:
        write_binary("sync", file_path, raw_data)

    def _async() -> Awaitable[None]:
        return write_binary("async", file_path, raw_data)

    if mode == "sync":
        _sync()
        return None
    else:
        return _async()
