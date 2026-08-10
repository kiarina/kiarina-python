def normalize_mime_type(mime_type: str) -> str:
    if not mime_type:
        return mime_type

    return mime_type.split(";")[0].strip().lower()
