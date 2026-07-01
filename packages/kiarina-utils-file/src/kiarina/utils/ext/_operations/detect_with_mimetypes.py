from mimetypes import guess_extension

from .._utils.normalize_mime_type import normalize_mime_type


def detect_with_mimetypes(mime_type: str) -> str | None:
    mime_type = normalize_mime_type(mime_type)

    if ext := guess_extension(mime_type, strict=False):
        return ext.lower()

    return None
