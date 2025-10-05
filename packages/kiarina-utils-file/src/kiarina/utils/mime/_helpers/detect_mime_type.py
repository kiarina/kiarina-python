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
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
    options: MimeDetectionOptions | None = None,
) -> str | None: ...


@overload
def detect_mime_type(
    *,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
    options: MimeDetectionOptions | None = None,
    default: str,
) -> str: ...


def detect_mime_type(
    *,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
    options: MimeDetectionOptions | None = None,
    default: str | None = None,
) -> str | None:
    """
    Detect the MIME type of a file or data stream using multiple detection methods.

    This function employs a multi-stage approach to determine the MIME type with high accuracy:

    Detection Strategy:
        1. **Content-based detection**: Uses `puremagic` to analyze raw data or file streams
           by examining file headers and magic bytes for precise identification.
        2. **Custom dictionary lookup**: Matches file extensions against a configurable
           mapping that handles complex cases like multi-part extensions (.tar.gz).
        3. **Standard library fallback**: Uses Python's built-in `mimetypes` module
           for standard file extension to MIME type mapping.

    All detected MIME types are automatically normalized using configurable aliases
    to ensure consistency with modern standards (e.g., "application/x-yaml" → "application/yaml").

    Args:
        raw_data (bytes | None): Raw binary data to analyze. Takes precedence over stream
            if both are provided.
        stream (BinaryIO | None): Binary file stream to analyze. Used when raw_data is None.
        file_name_hint (str | os.PathLike[str] | None): File name or path used as a hint
            for extension-based detection. Required when raw_data and stream are None.
        options (MimeDetectionOptions | None): Optional configuration for detection behavior.
            All fields are optional and will be merged with default settings.
            See `MimeDetectionOptions` for available options.
        default (str | None): Default MIME type to return if detection fails. Default is None.

    Returns:
        (str | None): The detected and normalized MIME type, or default if detection fails.

    Note:
        At least one of raw_data, stream, or file_name_hint must be provided.
        Content-based detection (raw_data/stream) is more reliable than extension-based detection.

    Examples:
        >>> # Basic usage
        >>> detect_mime_type(raw_data=b"\\x89PNG\\r\\n\\x1a\\n")
        "image/png"

        >>> # With custom options
        >>> options = {"mime_aliases": {"application/x-yaml": "application/yaml"}}
        >>> detect_mime_type(file_name_hint="config.yaml", options=options)
        "application/yaml"

        >>> # With default value
        >>> detect_mime_type(file_name_hint="unknown.xyz", default="application/octet-stream")
        "application/octet-stream"
    """
    # Extract options
    options = options or {}
    mime_aliases = options.get("mime_aliases")
    custom_mime_types = options.get("custom_mime_types")
    multi_extensions = options.get("multi_extensions")
    archive_extensions = options.get("archive_extensions")
    compression_extensions = options.get("compression_extensions")
    encryption_extensions = options.get("encryption_extensions")

    # Try to detect MIME type using puremagic
    if raw_data is not None or stream is not None:
        if mime_type := detect_with_puremagic(
            raw_data=raw_data, stream=stream, file_name_hint=file_name_hint
        ):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    # Try to detect MIME type using a dictionary based on file name hint
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

    # Try to detect MIME type using the mimetypes module
    if file_name_hint is not None:
        if mime_type := detect_with_mimetypes(file_name_hint):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    # If no MIME type is found, return default
    logger.debug(f"No MIME type found for file: {file_name_hint}")
    return default
