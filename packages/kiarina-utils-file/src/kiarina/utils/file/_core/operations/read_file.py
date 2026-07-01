import os
from collections.abc import Awaitable
from typing import Literal, overload

from kiarina.utils.mime import detect_mime_type

from ..models.file_blob import FileBlob
from ..utils.read_binary import read_binary


@overload
def read_file(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob | None = None,
) -> FileBlob | None: ...


@overload
def read_file(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob | None = None,
) -> Awaitable[FileBlob | None]: ...


def read_file(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob | None = None,
) -> FileBlob | None | Awaitable[FileBlob | None]:

    def _after(raw_data: bytes | None) -> FileBlob | None:
        if raw_data is None:
            return default

        mime_type = detect_mime_type(
            file_name_hint=file_path,
            raw_data=raw_data,
            default=fallback_mime_type,
        )

        return FileBlob(file_path, mime_type=mime_type, raw_data=raw_data)

    def _sync() -> FileBlob | None:
        raw_data = read_binary("sync", file_path)
        return _after(raw_data)

    async def _async() -> FileBlob | None:
        raw_data = await read_binary("async", file_path)
        return _after(raw_data)

    if mode == "sync":
        return _sync()
    else:
        return _async()
