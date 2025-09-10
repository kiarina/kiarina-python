import pytest

from kiarina.utils.encoding import normalize_newlines


# fmt: off
@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("", ""),  # Empty string
        ("Hello World", "Hello World"),  # No line breaks
        ("line1\nline2\nline3", "line1\nline2\nline3"),  # Unix style (multiple lines, unchanged)
        ("line1\r\nline2\r\nline3", "line1\nline2\nline3"),  # Windows style (multiple lines)
        ("line1\rline2\rline3", "line1\nline2\nline3"),  # Mac style (multiple lines)
        ("start\r\nwindows\rmac\nunix\r\n\rend", "start\nwindows\nmac\nunix\n\nend"),  # Mixed style
    ]
)
# fmt: on
def test_normalize_newlines(input_text, expected):
    """normalize_newlines 関数の包括的テスト"""
    result = normalize_newlines(input_text)
    assert result == expected
