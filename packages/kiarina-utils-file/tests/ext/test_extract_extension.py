import pytest

import kiarina.utils.ext as ke


# fmt: off
@pytest.mark.parametrize(
    "file_name_hint,expected",
    [
        # Normal extensions
        ("file.txt", ".txt"),
        ("document.pdf", ".pdf"),
        ("image.jpg", ".jpg"),
        # Multiple extensions
        ("archive.tar.gz", ".tar.gz"),
        ("backup.tar.bz2", ".tar.bz2"),
        ("encrypted.tar.gz.gpg", ".tar.gz.gpg"),
        # URL format
        ("https://example.com/file.txt?param=value", ".txt"),
        ("https://example.com/archive.tar.gz#section", ".tar.gz"),
        # With path
        ("/path/to/file.json", ".json"),
        ("../relative/path/data.csv", ".csv"),
        # No extension
        ("README", None),
        ("Makefile", None),
        # Empty string
        ("", None),
        # Files starting with dot (hidden files)
        (".gitignore", None),
        (".bashrc", None),
        # Mixed case (converted to lowercase)
        ("FILE.TXT", ".txt"),
        ("Document.PDF", ".pdf"),
    ],
)
# fmt: on
def test_extract_extension(file_name_hint, expected):
    assert ke.extract_extension(file_name_hint) == expected
