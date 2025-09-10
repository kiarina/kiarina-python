import pytest

from kiarina.utils.ext._utils.normalize_extension import normalize_extension


# fmt: off
@pytest.mark.parametrize(
    "extension,expected",
    [
        # Test dot normalization - extension without dot
        ("txt", ".txt"),
        ("custom", ".custom"),
        # Test dot normalization - extension with dot (should remain unchanged)
        (".txt", ".txt"),
        (".custom", ".custom"),
        # Test case normalization - uppercase extension
        ("TXT", ".txt"),
        ("CUSTOM", ".custom"),
        (".TXT", ".txt"),
        (".CUSTOM", ".custom"),
        # Test whitespace handling
        (" txt ", ".txt"),
        (" custom ", ".custom"),
        (" .txt ", ".txt"),
        (" .custom ", ".custom"),
        # Test mixed case and whitespace
        (" Txt ", ".txt"),
        (" Custom ", ".custom"),
        (" .Txt ", ".txt"),
        (" .Custom ", ".custom"),
        # Edge cases
        ("", ""),
        (".", "."),
        (" ", ""),
        ("  .  ", "."),
    ],
)
# fmt: on
def test_normalize_extension(extension, expected):
    assert normalize_extension(extension) == expected
