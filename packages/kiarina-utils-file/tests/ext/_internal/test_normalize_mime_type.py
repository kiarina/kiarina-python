import pytest

from kiarina.utils.ext._utils.normalize_mime_type import normalize_mime_type


# fmt: off
@pytest.mark.parametrize(
    "mime_type,expected",
    [
        # MIME type with charset parameter
        ("text/html; charset=utf-8", "text/html"),
        # Uppercase MIME type
        ("APPLICATION/JSON", "application/json"),
        # MIME type with quality parameter
        ("image/jpeg; quality=85", "image/jpeg"),
        # MIME type with multiple parameters
        ("text/plain; charset=utf-8; boundary=something", "text/plain"),
        # Simple MIME type (no parameters)
        ("image/png", "image/png"),
        # MIME type with spaces around semicolon
        ("text/css ; charset=utf-8", "text/css"),
        # Empty string
        ("", ""),
    ],
)
# fmt: on
def test_normalize_mime_type(mime_type: str, expected: str) -> None:
    assert normalize_mime_type(mime_type) == expected
