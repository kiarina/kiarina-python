import pytest

from kiarina.utils.ext._utils.normalize_extension import normalize_extension


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
def test_normalize_extension(extension: str, expected: str) -> None:
    assert normalize_extension(extension) == expected
