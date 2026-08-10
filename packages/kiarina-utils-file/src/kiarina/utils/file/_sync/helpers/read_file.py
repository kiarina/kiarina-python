import os
from typing import overload

from ..._core.models.file_blob import FileBlob
from ..._core.operations.read_file import read_file as _read_file


@overload
def read_file(
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
) -> FileBlob | None: ...


@overload
def read_file(
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob,
) -> FileBlob: ...


def read_file(
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob | None = None,
) -> FileBlob | None:
    return _read_file(
        "sync", file_path, fallback_mime_type=fallback_mime_type, default=default
    )
