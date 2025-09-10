import pytest

import kiarina.utils.ext as ke


# fmt: off
@pytest.mark.parametrize(
    "mime_type, expected",
    [
        ("text/css", ".css"),
        ("text/html", ".html"),
        ("text/html; charset=utf-8", ".html"),
        ("text/nonexistent", None),
        ("text/plain", ".txt"),
        ("text/xml", ".xml"),
        ("image/jpeg", ".jpg"),
        ("image/png", ".png"),
        ("application/custom", ".custom"),
        ("application/json", ".json"),
        ("application/pdf", ".pdf"),
        ("application/yaml", ".yaml"),
        ("", None),
    ],
)
# fmt: on
def test_detect_extension(mime_type, expected):
    result = ke.detect_extension(
        mime_type=mime_type,
        custom_extensions={"application/custom": ".custom"},
    )
    assert result == expected
