import pytest

from kiarina.utils.ext._utils.clean_url_path import clean_url_path


# fmt: off
@pytest.mark.parametrize(
    "input_path,expected",
    [
        # URL with query parameter and fragment
        ("https://example.com/file.txt?param=value#section", "https://example.com/file.txt"),
        # URL with only query parameter
        ("https://example.com/file.txt?param=value", "https://example.com/file.txt"),
        # URL with only fragment
        ("https://example.com/file.txt#section", "https://example.com/file.txt"),
        # file:// URL with query parameter
        ("file:///path/to/file.txt?query=test", "file:///path/to/file.txt"),
        # Local path (should remain unchanged)
        ("/local/path/file.txt", "/local/path/file.txt"),
        # URL without parameters (should remain unchanged)
        ("https://example.com/file.txt", "https://example.com/file.txt"),
        # Empty string
        ("", ""),
        # Complex URL with multiple query parameters
        ("https://api.example.com/data.json?key=value&other=param#hash", "https://api.example.com/data.json"),
    ],
)
# fmt: on
def test_clean_url_path(input_path, expected):
    assert clean_url_path(input_path) == expected
