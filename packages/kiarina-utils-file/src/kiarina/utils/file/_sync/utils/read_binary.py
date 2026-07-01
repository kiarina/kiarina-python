import os
from typing import overload

from ..._core.utils.read_binary import read_binary as _read_binary


@overload
def read_binary(file_path: str | os.PathLike[str]) -> bytes | None: ...


@overload
def read_binary(file_path: str | os.PathLike[str], *, default: bytes) -> bytes: ...


def read_binary(
    file_path: str | os.PathLike[str], *, default: bytes | None = None
) -> bytes | None:
    return _read_binary("sync", file_path, default=default)
