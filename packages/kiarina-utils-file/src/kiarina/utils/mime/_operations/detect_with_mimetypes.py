import logging
import os
from mimetypes import guess_type

logger = logging.getLogger(__name__)


def detect_with_mimetypes(file_name_hint: str | os.PathLike[str]) -> str | None:
    mime_type, _ = guess_type(file_name_hint, strict=False)

    return mime_type
