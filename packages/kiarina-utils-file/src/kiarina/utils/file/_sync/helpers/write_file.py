import os

from ..._core.models.file_blob import FileBlob
from ..._core.operations.write_file import write_file as _write_file


def write_file(
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> None:
    _write_file("sync", file_blob, file_path=file_path)
