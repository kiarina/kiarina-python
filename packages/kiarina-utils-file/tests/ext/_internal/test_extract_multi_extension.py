import pytest

from kiarina.utils.ext._operations.extract_multi_extension import (
    extract_multi_extension,
)


# fmt: off
@pytest.mark.parametrize(
    "file_name_hint,expected",
    [
        # Known multi-extensions
        ("archive.tar.gz", ".tar.gz"),
        ("data.tar.bz2", ".tar.bz2"),
        ("backup.tar.xz", ".tar.xz"),
        ("file.tar.gz.gpg", ".tar.gz.gpg"),
        ("document.tar.bz2.gpg", ".tar.bz2.gpg"),
        ("package.tar.xz.gpg", ".tar.xz.gpg"),

        # Dynamic detection - archive + compression
        ("test.tar.lzma", ".tar.lzma"),
        ("data.tar.zst", ".tar.zst"),
        ("archive.tar.z", ".tar.z"),
        ("backup.tar.lzo", ".tar.lzo"),

        # Single extension (not multi-extension)
        ("file.txt", None),
        ("image.jpg", None),
        ("data.gz", None),

        # Patterns that are not multi-extensions
        ("file.doc.backup", None),
        ("test.config.old", None),

        # Cases with path separators
        ("/path/to/archive.tar.gz", ".tar.gz"),
        ("./relative/data.tar.bz2", ".tar.bz2"),

        # Empty strings and edge cases
        ("", None),
        ("noextension", None),
        (".hidden", None),
        ("file.", None),
    ],
)
# fmt: on
def test_main(file_name_hint, expected):
    assert extract_multi_extension(file_name_hint) == expected
