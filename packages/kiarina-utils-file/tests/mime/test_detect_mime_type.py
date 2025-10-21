import pytest

import kiarina.utils.mime as km


# fmt: off
@pytest.mark.parametrize(
    "raw_data,file_name_hint,expected_mime_type",
    [
        (b"Hello, World!", "test.txt", "text/plain"),
        (b"---\ntitle: hello\n---\ntest markdown", "test.md", "text/markdown"),  # Extension takes precedence
        (None, "test.md", "text/markdown"),
        (b'{"key": "value"}', "config.json", "application/json"),
        (b"<html><body>Test</body></html>", "index.html", "text/html"),
        (b"\x89PNG\r\n\x1a\n", "image.png", "image/png"),
        (b'{"test": true}', None, "application/json"),
        (b"key: value", "settings.yaml", "application/yaml"),
        (b"unknown content", "unknown.unknownext", None),
        (b"", "empty.txt", "text/plain"),
        (b"// this is type script", "app.ts", "application/x-typescript"),
    ],
    ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
)
# fmt: on
def test_detect_mime_type(raw_data, file_name_hint, expected_mime_type):
    result = km.detect_mime_type(
        file_name_hint=file_name_hint,
        raw_data=raw_data,
    )
    assert result == expected_mime_type
