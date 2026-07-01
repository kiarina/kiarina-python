import os

from ..._core.utils.write_text import write_text as _write_text


async def write_text(file_path: str | os.PathLike[str], raw_text: str) -> None:
    await _write_text("async", file_path, raw_text)
