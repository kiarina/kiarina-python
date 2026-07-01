import os
from typing import overload

from ..._core.operations.read_markdown import read_markdown as _read_markdown
from ..._core.types.markdown_content import MarkdownContent


@overload
def read_markdown(
    file_path: str | os.PathLike[str],
) -> MarkdownContent | None: ...


@overload
def read_markdown(
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent,
) -> MarkdownContent: ...


def read_markdown(
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> MarkdownContent | None:
    return _read_markdown("sync", file_path, default=default)
