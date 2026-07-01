import logging
from typing import overload

from .._operations.detect_with_dictionary import detect_with_dictionary
from .._operations.detect_with_mimetypes import detect_with_mimetypes

logger = logging.getLogger(__name__)


@overload
def detect_extension(
    mime_type: str,
    *,
    custom_extensions: dict[str, str] | None = None,
) -> str | None: ...


@overload
def detect_extension(
    mime_type: str,
    *,
    custom_extensions: dict[str, str] | None = None,
    default: str,
) -> str: ...


def detect_extension(
    mime_type: str,
    *,
    custom_extensions: dict[str, str] | None = None,
    default: str | None = None,
) -> str | None:
    if ext := detect_with_dictionary(mime_type, custom_extensions=custom_extensions):
        return ext

    if ext := detect_with_mimetypes(mime_type):
        return ext

    logger.debug(f"No extension found for MIME type: {mime_type}")
    return default
