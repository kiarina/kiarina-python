import os

from ..._core.models.file_blob import FileBlob
from ..._core.operations.write_file import write_file as _write_file


async def write_file(
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> None:
    await _write_file("async", file_blob, file_path=file_path)
