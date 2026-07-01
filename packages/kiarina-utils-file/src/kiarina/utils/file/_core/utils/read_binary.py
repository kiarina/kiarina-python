import os
from collections.abc import Awaitable
from typing import Literal, overload

import aiofiles
from filelock import AsyncFileLock, FileLock

from .get_lock_file_path import get_lock_file_path


@overload
def read_binary(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    *,
    default: bytes | None = None,
) -> bytes | None: ...


@overload
def read_binary(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    *,
    default: bytes | None = None,
) -> Awaitable[bytes | None]: ...


def read_binary(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    *,
    default: bytes | None = None,
) -> bytes | None | Awaitable[bytes | None]:
    file_path = os.path.expanduser(os.path.expandvars(os.fspath(file_path)))

    if os.path.lexists(file_path):  # Check if path exists (including broken symlinks)
        file_path = os.path.realpath(file_path)

    lock_file_path = get_lock_file_path(file_path)

    def _check_file_exists() -> bool:
        if not os.path.exists(file_path):
            return False

        if os.path.isdir(file_path):
            raise IsADirectoryError(f"{file_path} is a directory")

        return True

    def _sync() -> bytes | None:
        lock = FileLock(lock_file_path)

        with lock:
            if not _check_file_exists():
                return default

            with open(file_path, "rb") as f:
                return f.read()

    async def _async() -> bytes | None:
        lock = AsyncFileLock(lock_file_path)

        async with lock:
            if not _check_file_exists():
                return default

            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()

    if mode == "sync":
        return _sync()
    else:
        return _async()
