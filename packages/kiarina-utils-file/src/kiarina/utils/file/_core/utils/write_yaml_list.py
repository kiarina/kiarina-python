import os
from collections.abc import Awaitable
from typing import Any, Literal, overload

import yaml

from .write_text import write_text


@overload
def write_yaml_list(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    yaml_list: list[Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> None: ...


@overload
def write_yaml_list(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    yaml_list: list[Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> Awaitable[None]: ...


def write_yaml_list(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    yaml_list: list[Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> None | Awaitable[None]:
    yaml_text = yaml.dump(yaml_list, allow_unicode=allow_unicode, sort_keys=sort_keys)

    def _sync() -> None:
        write_text("sync", file_path, yaml_text)

    def _async() -> Awaitable[None]:
        return write_text("async", file_path, yaml_text)

    if mode == "sync":
        _sync()
        return None
    else:
        return _async()
