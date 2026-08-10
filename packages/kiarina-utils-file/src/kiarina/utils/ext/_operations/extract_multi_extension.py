import os
import pathlib

from .._settings import settings_manager
from .._utils.clean_url_path import clean_url_path


def extract_multi_extension(
    file_name_hint: str | os.PathLike[str],
    *,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
) -> str | None:
    file_name_hint = os.path.expanduser(os.path.expandvars(os.fspath(file_name_hint)))

    if not file_name_hint:
        return None

    file_name_hint = clean_url_path(file_name_hint)

    filename_lower = pathlib.Path(file_name_hint).name.lower()

    settings = settings_manager.settings

    if multi_extensions is None:
        multi_exts = settings.multi_extensions
    else:
        multi_exts = settings.multi_extensions | multi_extensions

    if archive_extensions is None:
        archive_exts = settings.archive_extensions
    else:
        archive_exts = settings.archive_extensions | archive_extensions

    if compression_extensions is None:
        compression_exts = settings.compression_extensions
    else:
        compression_exts = settings.compression_extensions | compression_extensions

    if encryption_extensions is None:
        encryption_exts = settings.encryption_extensions
    else:
        encryption_exts = settings.encryption_extensions | encryption_extensions

    for multi_ext in sorted(multi_exts, key=len, reverse=True):
        if filename_lower.endswith(multi_ext):
            return multi_ext.lower()

    parts = filename_lower.split(".")

    if len(parts) >= 3:  # At least name.ext1.ext2 format
        max_parts = (
            settings.max_multi_extension_parts + 1
        )  # +1 because range is exclusive

        for i in range(2, min(len(parts), max_parts)):
            candidate_ext = "." + ".".join(parts[-i:])
            ext_parts = candidate_ext[1:].split(".")

            if len(ext_parts) >= 2:
                first_ext = f".{ext_parts[0]}"
                remaining_exts = [f".{ext}" for ext in ext_parts[1:]]

                if first_ext in archive_exts and any(
                    (ext in compression_exts or ext in encryption_exts)
                    for ext in remaining_exts
                ):
                    return candidate_ext.lower()

    return None
