from .._operations.detect_with_charset_normalizer import detect_with_charset_normalizer
from .._operations.detect_with_fallback import detect_with_fallback
from .._operations.detect_with_nkf import detect_with_nkf
from .._operations.should_use_nkf import should_use_nkf
from .._settings import settings_manager


def detect_encoding(
    raw_data: bytes,
    *,
    use_nkf: bool | None = None,
    confidence_threshold: float | None = None,
    fallback_encodings: list[str] | None = None,
) -> str | None:
    if use_nkf is None:
        use_nkf = settings_manager.settings.use_nkf

    if use_nkf is None:
        use_nkf = should_use_nkf()

    if use_nkf:
        if encoding := detect_with_nkf(raw_data):
            return encoding

    if encoding := detect_with_charset_normalizer(
        raw_data, confidence_threshold=confidence_threshold
    ):
        return encoding

    if encoding := detect_with_fallback(
        raw_data, fallback_encodings=fallback_encodings
    ):
        return encoding

    return None
