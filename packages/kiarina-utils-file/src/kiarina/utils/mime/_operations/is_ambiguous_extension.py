import os

from ..settings import settings_manager


def is_ambiguous_extension(
    file_name_hint: str | os.PathLike[str],
    *,
    ambiguous_extensions: set[str] | None = None,
) -> bool:
    """
    Check if the file extension is ambiguous.

    Ambiguous extensions require content-based MIME type detection because
    the extension alone cannot determine the correct type. For example,
    .ts could be TypeScript source code or MPEG-2 Transport Stream video.

    The provided extensions are merged with the default settings, allowing
    for both global configuration and per-call customization.

    Args:
        file_name_hint (str | os.PathLike[str]): File name or path to check
        ambiguous_extensions (set[str] | None): Set of ambiguous extensions.
            If None, uses only the default settings. If provided, merges with
            default settings.

    Returns:
        bool: True if the extension is ambiguous, False otherwise

    Examples:
        >>> # Using default settings (includes .ts)
        >>> is_ambiguous_extension("app.ts")
        True

        >>> # Using custom extensions (merged with defaults)
        >>> is_ambiguous_extension("app.custom", ambiguous_extensions={".custom"})
        True

        >>> # File not in ambiguous list
        >>> is_ambiguous_extension("app.js")
        False

        >>> # Case insensitive matching
        >>> is_ambiguous_extension("App.TS")
        True
    """
    # Merge with settings default
    settings = settings_manager.settings

    if ambiguous_extensions is None:
        merged_extensions = settings.ambiguous_extensions
    else:
        merged_extensions = settings.ambiguous_extensions | ambiguous_extensions

    if not merged_extensions:
        return False

    file_name_lower = str(file_name_hint).lower()

    return any(file_name_lower.endswith(ext.lower()) for ext in merged_extensions)
