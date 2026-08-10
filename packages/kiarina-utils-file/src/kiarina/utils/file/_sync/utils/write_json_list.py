import os
from typing import Any

from ..._core.utils.write_json_list import write_json_list as _write_json_list


def write_json_list(
    file_path: str | os.PathLike[str],
    json_list: list[Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None:
    _write_json_list(
        "sync",
        file_path,
        json_list,
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
    )
