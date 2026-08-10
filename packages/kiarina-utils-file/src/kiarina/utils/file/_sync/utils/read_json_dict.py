import os
from typing import Any, overload

from ..._core.utils.read_json_dict import read_json_dict as _read_json_dict


@overload
def read_json_dict(file_path: str | os.PathLike[str]) -> dict[str, Any] | None: ...


@overload
def read_json_dict(
    file_path: str | os.PathLike[str], *, default: dict[str, Any]
) -> dict[str, Any]: ...


def read_json_dict(
    file_path: str | os.PathLike[str], *, default: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    return _read_json_dict("sync", file_path, default=default)
