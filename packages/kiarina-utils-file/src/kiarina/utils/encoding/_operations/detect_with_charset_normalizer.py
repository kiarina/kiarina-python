import logging

from charset_normalizer import detect

from .._settings import settings_manager

logger = logging.getLogger(__name__)


def detect_with_charset_normalizer(
    raw_data: bytes, *, confidence_threshold: float | None = None
) -> str | None:
    if not raw_data:
        return None

    if confidence_threshold is None:
        confidence_threshold = (
            settings_manager.settings.charset_normalizer_confidence_threshold
        )

    result = detect(raw_data)

    if (
        result["encoding"]
        and result["confidence"]
        and result["confidence"] >= confidence_threshold
    ):
        return result["encoding"].lower()

    return None
