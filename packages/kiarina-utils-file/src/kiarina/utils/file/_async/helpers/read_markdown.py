import os
from typing import overload

from ..._core.operations.read_markdown import read_markdown as _read_markdown
from ..._core.types.markdown_content import MarkdownContent


@overload
async def read_markdown(
    file_path: str | os.PathLike[str],
) -> MarkdownContent | None: ...


@overload
async def read_markdown(
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent,
) -> MarkdownContent: ...


async def read_markdown(
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> MarkdownContent | None:
    return await _read_markdown("async", file_path, default=default)
