from .._settings import settings_manager
from .._utils.normalize_newlines import normalize_newlines
from .detect_encoding import detect_encoding


def decode_binary_to_text(
    raw_data: bytes,
    *,
    use_nkf: bool | None = None,
    fallback_encodings: list[str] | None = None,
    default_encoding: str | None = None,
) -> str:
    if default_encoding is None:
        default_encoding = settings_manager.settings.default_encoding

    encoding = detect_encoding(
        raw_data, use_nkf=use_nkf, fallback_encodings=fallback_encodings
    )

    if encoding is None:
        encoding = default_encoding

    if encoding == "ascii":
        encoding = "utf-8"

    text = raw_data.decode(encoding, errors="replace")

    return normalize_newlines(text)
