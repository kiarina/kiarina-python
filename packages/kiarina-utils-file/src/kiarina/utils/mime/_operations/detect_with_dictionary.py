import logging
import os

import kiarina.utils.ext as ke

from .._settings import settings_manager

logger = logging.getLogger(__name__)


def detect_with_dictionary(
    file_name_hint: str | os.PathLike[str],
    *,
    custom_mime_types: dict[str, str] | None = None,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
) -> str | None:
    ext = ke.extract_extension(
        file_name_hint,
        multi_extensions=multi_extensions,
        archive_extensions=archive_extensions,
        compression_extensions=compression_extensions,
        encryption_extensions=encryption_extensions,
    )

    if not ext:
        return None

    if custom_mime_types is not None and ext in custom_mime_types:
        return custom_mime_types[ext]

    settings = settings_manager.settings

    if ext in settings.custom_mime_types:
        return settings.custom_mime_types[ext]

    return None
