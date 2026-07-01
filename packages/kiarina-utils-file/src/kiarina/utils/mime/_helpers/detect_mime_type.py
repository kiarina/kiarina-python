import logging
import os
from typing import BinaryIO, overload

from .._operations.detect_with_dictionary import detect_with_dictionary
from .._operations.detect_with_mimetypes import detect_with_mimetypes
from .._operations.detect_with_puremagic import detect_with_puremagic
from .._types.mime_detection_options import MimeDetectionOptions
from .apply_mime_alias import apply_mime_alias

logger = logging.getLogger(__name__)


@overload
def detect_mime_type(
    *,
    file_name_hint: str | os.PathLike[str] | None = None,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    options: MimeDetectionOptions | None = None,
) -> str | None: ...


@overload
def detect_mime_type(
    *,
    file_name_hint: str | os.PathLike[str] | None = None,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    options: MimeDetectionOptions | None = None,
    default: str,
) -> str: ...


def detect_mime_type(
    *,
    file_name_hint: str | os.PathLike[str] | None = None,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    options: MimeDetectionOptions | None = None,
    default: str | None = None,
) -> str | None:
    options = options or {}
    mime_aliases = options.get("mime_aliases")
    custom_mime_types = options.get("custom_mime_types")
    multi_extensions = options.get("multi_extensions")
    archive_extensions = options.get("archive_extensions")
    compression_extensions = options.get("compression_extensions")
    encryption_extensions = options.get("encryption_extensions")

    if file_name_hint is not None:
        if mime_type := detect_with_dictionary(
            file_name_hint,
            custom_mime_types=custom_mime_types,
            multi_extensions=multi_extensions,
            archive_extensions=archive_extensions,
            compression_extensions=compression_extensions,
            encryption_extensions=encryption_extensions,
        ):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

        if mime_type := detect_with_mimetypes(file_name_hint):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    if raw_data is not None or stream is not None:
        if mime_type := detect_with_puremagic(
            raw_data=raw_data,
            stream=stream,
            file_name_hint=file_name_hint,
        ):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    logger.debug(f"No MIME type found for file: {file_name_hint}")
    return default
