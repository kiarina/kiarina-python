import os
from typing import Any, overload

from ..._core.utils.read_yaml_list import read_yaml_list as _read_yaml_list


@overload
async def read_yaml_list(
    file_path: str | os.PathLike[str],
) -> list[Any] | None: ...


@overload
async def read_yaml_list(
    file_path: str | os.PathLike[str], *, default: list[Any]
) -> list[Any]: ...


async def read_yaml_list(
    file_path: str | os.PathLike[str], *, default: list[Any] | None = None
) -> list[Any] | None:
    return await _read_yaml_list("async", file_path, default=default)
