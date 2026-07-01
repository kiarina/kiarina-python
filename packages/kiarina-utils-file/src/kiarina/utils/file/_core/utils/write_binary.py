import asyncio
import logging
import os
import tempfile
from collections.abc import Awaitable
from typing import Literal, overload

import aiofiles
from filelock import AsyncFileLock, FileLock

from .get_lock_file_path import get_lock_file_path

logger = logging.getLogger(__name__)


@overload
def write_binary(
    mode: Literal["sync"], file_path: str | os.PathLike[str], raw_data: bytes
) -> None: ...


@overload
def write_binary(
    mode: Literal["async"], file_path: str | os.PathLike[str], raw_data: bytes
) -> Awaitable[None]: ...


def write_binary(
    mode: Literal["sync", "async"], file_path: str | os.PathLike[str], raw_data: bytes
) -> None | Awaitable[None]:
    file_path = os.path.expanduser(os.path.expandvars(os.fspath(file_path)))

    if os.path.lexists(file_path):  # Check if path exists (including broken symlinks)
        file_path = os.path.realpath(file_path)

    if dirname := os.path.dirname(file_path):
        os.makedirs(dirname, exist_ok=True)

    lock_file_path = get_lock_file_path(file_path)

    fd, temp_file_path = tempfile.mkstemp(
        dir=dirname if dirname else None,
        prefix=".write_binary_",
        suffix=".tmp",
    )
    os.close(fd)

    def _cleanup_temp_file() -> None:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

    def _preserve_permissions() -> None:
        if os.path.exists(file_path):
            try:
                original_stat = os.stat(file_path)
                os.chmod(temp_file_path, original_stat.st_mode)

                if hasattr(os, "chown"):
                    try:
                        os.chown(
                            temp_file_path, original_stat.st_uid, original_stat.st_gid
                        )
                    except (OSError, PermissionError) as e:
                        logger.debug(
                            f"Failed to preserve file ownership for {file_path}: {e}"
                        )

            except (OSError, FileNotFoundError):
                pass

    def _sync() -> None:
        lock = FileLock(lock_file_path)

        try:
            with lock:
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(raw_data)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())

                _preserve_permissions()

                os.replace(temp_file_path, file_path)

        except Exception:
            _cleanup_temp_file()
            raise

    async def _async() -> None:
        lock = AsyncFileLock(lock_file_path)

        try:
            async with lock:
                async with aiofiles.open(temp_file_path, "wb") as temp_file:
                    await temp_file.write(raw_data)
                    await temp_file.flush()
                    await asyncio.to_thread(os.fsync, temp_file.fileno())

                _preserve_permissions()

                os.replace(temp_file_path, file_path)

        except Exception:
            _cleanup_temp_file()
            raise

    if mode == "sync":
        _sync()
        return None
    else:
        return _async()
