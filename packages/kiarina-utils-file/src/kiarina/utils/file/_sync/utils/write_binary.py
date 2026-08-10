import os

from ..._core.utils.write_binary import write_binary as _write_binary


def write_binary(file_path: str | os.PathLike[str], raw_data: bytes) -> None:
    _write_binary("sync", file_path, raw_data)
