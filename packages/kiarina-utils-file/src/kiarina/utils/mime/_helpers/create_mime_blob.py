from .._models.mime_blob import MIMEBlob
from .detect_mime_type import detect_mime_type


def create_mime_blob(
    raw_data: bytes, *, fallback_mime_type: str = "application/octet-stream"
) -> MIMEBlob:
    mime_type = detect_mime_type(raw_data=raw_data, default=fallback_mime_type)
    return MIMEBlob(mime_type=mime_type, raw_data=raw_data)
