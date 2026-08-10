import os
from typing import overload

from ..._core.utils.read_binary import read_binary as _read_binary


@overload
async def read_binary(file_path: str | os.PathLike[str]) -> bytes | None: ...


@overload
async def read_binary(
    file_path: str | os.PathLike[str], *, default: bytes
) -> bytes: ...


async def read_binary(
    file_path: str | os.PathLike[str], *, default: bytes | None = None
) -> bytes | None:
    return await _read_binary("async", file_path, default=default)
