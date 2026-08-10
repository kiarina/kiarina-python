from .._settings import settings_manager
from .._utils.normalize_extension import normalize_extension
from .._utils.normalize_mime_type import normalize_mime_type


def detect_with_dictionary(
    mime_type: str,
    *,
    custom_extensions: dict[str, str] | None = None,
) -> str | None:
    mime_type = normalize_mime_type(mime_type)

    if custom_extensions is not None and mime_type in custom_extensions:
        return normalize_extension(custom_extensions[mime_type])

    settings = settings_manager.settings

    if mime_type in settings.custom_extensions:
        return normalize_extension(settings.custom_extensions[mime_type])

    return None
