from .._settings import settings_manager


def detect_with_fallback(
    raw_data: bytes,
    *,
    fallback_encodings: list[str] | None = None,
) -> str | None:
    if not raw_data:
        return None

    if fallback_encodings is None:
        fallback_encodings = settings_manager.settings.fallback_encodings

    max_size = settings_manager.settings.max_sample_size

    if len(raw_data) > max_size:
        sample_data = raw_data[:max_size]
    else:
        sample_data = raw_data

    for enc in fallback_encodings:
        try:
            sample_data.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue

    return None
