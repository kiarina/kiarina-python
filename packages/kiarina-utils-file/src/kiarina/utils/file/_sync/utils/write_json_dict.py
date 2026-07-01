import os
from typing import Any

from ..._core.utils.write_json_dict import write_json_dict as _write_json_dict


def write_json_dict(
    file_path: str | os.PathLike[str],
    json_dict: dict[str, Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None:
    _write_json_dict(
        "sync",
        file_path,
        json_dict,
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
    )
