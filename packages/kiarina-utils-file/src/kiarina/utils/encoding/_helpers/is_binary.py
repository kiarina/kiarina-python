from .detect_encoding import detect_encoding


def is_binary(
    raw_data: bytes,
    *,
    use_nkf: bool | None = None,
    fallback_encodings: list[str] | None = None,
) -> bool:
    if not raw_data:
        return False

    encoding = detect_encoding(
        raw_data, use_nkf=use_nkf, fallback_encodings=fallback_encodings
    )

    return encoding is None
