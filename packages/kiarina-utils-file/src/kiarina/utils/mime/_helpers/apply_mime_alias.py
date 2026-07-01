from .._settings import settings_manager


def apply_mime_alias(
    mime_type: str, *, mime_aliases: dict[str, str] | None = None
) -> str:
    if mime_aliases is None:
        mime_aliases = settings_manager.settings.mime_aliases
    else:
        mime_aliases = {**settings_manager.settings.mime_aliases, **mime_aliases}

    return mime_aliases.get(mime_type, mime_type)
