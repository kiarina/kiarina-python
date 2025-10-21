import os

from ..settings import settings_manager


def should_skip_extension_detection(
    file_name_hint: str | os.PathLike[str],
    *,
    skip_extension_detection_suffixes: set[str] | None = None,
) -> bool:
    """
    Determine if extension-based MIME type detection should be skipped.

    This function checks if the file name ends with any of the specified suffixes
    that indicate ambiguous file extensions (e.g., .ts for TypeScript vs MPEG-2 TS).

    The provided suffixes are merged with the default settings, allowing for both
    global configuration and per-call customization.

    Args:
        file_name_hint (str | os.PathLike[str]): File name or path to check
        skip_extension_detection_suffixes (set[str] | None): Set of suffixes to skip
            extension-based detection for. If None, uses only the default settings.
            If provided, merges with default settings.

    Returns:
        bool: True if extension-based detection should be skipped, False otherwise

    Examples:
        >>> # Using default settings (includes .ts)
        >>> should_skip_extension_detection("app.ts")
        True

        >>> # Using custom suffixes (merged with defaults)
        >>> should_skip_extension_detection("app.custom", skip_extension_detection_suffixes={".custom"})
        True

        >>> # File not in skip list
        >>> should_skip_extension_detection("app.js")
        False

        >>> # Case insensitive matching
        >>> should_skip_extension_detection("App.TS")
        True
    """
    # Merge with settings default
    settings = settings_manager.settings

    if skip_extension_detection_suffixes is None:
        merged_suffixes = settings.skip_extension_detection_suffixes
    else:
        merged_suffixes = (
            settings.skip_extension_detection_suffixes
            | skip_extension_detection_suffixes
        )

    if not merged_suffixes:
        return False

    file_name_lower = str(file_name_hint).lower()

    return any(file_name_lower.endswith(suffix.lower()) for suffix in merged_suffixes)
