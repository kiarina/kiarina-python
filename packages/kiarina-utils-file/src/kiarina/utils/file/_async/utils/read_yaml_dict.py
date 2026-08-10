import os
from typing import Any, overload

from ..._core.utils.read_yaml_dict import read_yaml_dict as _read_yaml_dict


@overload
async def read_yaml_dict(
    file_path: str | os.PathLike[str],
) -> dict[str, Any] | None: ...


@overload
async def read_yaml_dict(
    file_path: str | os.PathLike[str], *, default: dict[str, Any]
) -> dict[str, Any]: ...


async def read_yaml_dict(
    file_path: str | os.PathLike[str], *, default: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    return await _read_yaml_dict("async", file_path, default=default)
