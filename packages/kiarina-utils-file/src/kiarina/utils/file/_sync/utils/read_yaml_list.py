import os
from typing import Any, overload

from ..._core.utils.read_yaml_list import read_yaml_list as _read_yaml_list


@overload
def read_yaml_list(file_path: str | os.PathLike[str]) -> list[Any] | None: ...


@overload
def read_yaml_list(
    file_path: str | os.PathLike[str], *, default: list[Any]
) -> list[Any]: ...


def read_yaml_list(
    file_path: str | os.PathLike[str], *, default: list[Any] | None = None
) -> list[Any] | None:
    return _read_yaml_list("sync", file_path, default=default)
