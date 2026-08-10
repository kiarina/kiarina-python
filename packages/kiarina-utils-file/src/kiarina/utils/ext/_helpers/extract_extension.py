import logging
import os
import pathlib
from typing import overload

from .._operations.extract_multi_extension import extract_multi_extension
from .._utils.clean_url_path import clean_url_path

logger = logging.getLogger(__name__)


@overload
def extract_extension(
    file_name_hint: str | os.PathLike[str],
    *,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
) -> str | None: ...


@overload
def extract_extension(
    file_name_hint: str | os.PathLike[str],
    *,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
    default: str,
) -> str: ...


def extract_extension(
    file_name_hint: str | os.PathLike[str],
    *,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
    default: str | None = None,
) -> str | None:
    file_name_hint = os.path.expanduser(os.path.expandvars(os.fspath(file_name_hint)))

    if not file_name_hint:
        return default

    file_name_hint = clean_url_path(file_name_hint)

    if multi_ext := extract_multi_extension(
        file_name_hint,
        multi_extensions=multi_extensions,
        archive_extensions=archive_extensions,
        compression_extensions=compression_extensions,
        encryption_extensions=encryption_extensions,
    ):
        return multi_ext

    if ext := pathlib.Path(file_name_hint).suffix:
        return ext.lower()

    logger.debug(f"No extension found for file name hint: {file_name_hint}")
    return default
