import os
from collections.abc import Awaitable
from typing import Literal, overload

from ..models.file_blob import FileBlob
from ..utils.write_binary import write_binary


@overload
def write_file(
    mode: Literal["sync"],
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> None: ...


@overload
def write_file(
    mode: Literal["async"],
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> Awaitable[None]: ...


def write_file(
    mode: Literal["sync", "async"],
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> None | Awaitable[None]:
    if file_path is None:
        file_path = file_blob.file_path

    def _sync() -> None:
        write_binary("sync", file_path, file_blob.raw_data)

    async def _async() -> None:
        await write_binary("async", file_path, file_blob.raw_data)

    if mode == "sync":
        _sync()
        return None
    else:
        return _async()
