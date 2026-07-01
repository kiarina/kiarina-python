import logging
import os
from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO

if TYPE_CHECKING:
    import puremagic

logger = logging.getLogger(__name__)

if not TYPE_CHECKING:
    try:
        import puremagic
    except ImportError:
        logger.debug("puremagic is not available.")
        puremagic = None  # type: ignore


def detect_with_puremagic(
    *,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
) -> str | None:
    if puremagic is None:
        return None

    if raw_data is not None and stream is not None:
        raise ValueError("Only one of 'raw_data' or 'stream' should be provided.")

    try:
        if raw_data is not None:
            if not raw_data:
                return None

            infos = puremagic.magic_stream(BytesIO(raw_data), filename=file_name_hint)

        elif stream is not None:
            infos = puremagic.magic_stream(stream, filename=file_name_hint)

        else:
            raise ValueError("Either 'raw_data' or 'stream' must be provided.")

        if infos:
            assert isinstance(infos[0].mime_type, str)
            return infos[0].mime_type

    except puremagic.PureError:
        logger.debug("Failed to detect MIME type with puremagic.", exc_info=True)

    return None
