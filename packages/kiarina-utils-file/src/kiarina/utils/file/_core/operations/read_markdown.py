import os
from collections.abc import Awaitable
from typing import Literal, overload

from ..types.markdown_content import MarkdownContent
from ..utils.read_text import read_text


@overload
def read_markdown(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> MarkdownContent | None: ...


@overload
def read_markdown(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> Awaitable[MarkdownContent | None]: ...


def read_markdown(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> MarkdownContent | None | Awaitable[MarkdownContent | None]:

    def _parse_markdown(raw_text: str | None) -> MarkdownContent | None:
        if raw_text is None:
            return default

        return MarkdownContent.from_text(raw_text)

    def _sync() -> MarkdownContent | None:
        raw_text = read_text("sync", file_path)
        return _parse_markdown(raw_text)

    async def _async() -> MarkdownContent | None:
        raw_text = await read_text("async", file_path)
        return _parse_markdown(raw_text)

    if mode == "sync":
        return _sync()
    else:
        return _async()
