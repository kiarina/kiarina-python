import pytest

from kiarina.utils.mime._operations.is_ambiguous_extension import (
    is_ambiguous_extension,
)


# fmt: off
@pytest.mark.parametrize(
    "file_name_hint,ambiguous_exts,expected",
    [
        # Basic matching
        ("app.ts", {".ts"}, True),
        ("app.js", {".ts"}, False),
        ("app.ts", set(), True),  # Empty set merges with defaults (.ts is in defaults)
        
        # Case insensitive matching
        ("App.TS", {".ts"}, True),
        ("APP.TS", {".ts"}, True),
        ("app.ts", {".TS"}, True),
        
        # Multiple extensions
        ("app.ts", {".ts", ".js"}, True),
        ("app.js", {".ts", ".js"}, True),
        ("app.py", {".ts", ".js"}, False),
        
        # Path with directories
        ("/path/to/app.ts", {".ts"}, True),
        ("./relative/app.ts", {".ts"}, True),
        ("C:\\Windows\\app.ts", {".ts"}, True),
        
        # Multi-part extensions
        ("archive.tar.gz", {".tar.gz"}, True),
        ("archive.tar.gz", {".gz"}, True),
        ("archive.tar.gz", {".tar"}, False),
        
        # Edge cases
        ("", {".ts"}, False),
        ("noextension", {".ts"}, False),
        (".hidden", {".hidden"}, True),
        ("file.", {".ts"}, False),
        
        # URL format
        ("https://example.com/app.ts", {".ts"}, True),
        ("https://example.com/app.ts?param=value", {".ts"}, False),  # Query params not handled
    ],
)
# fmt: on
def test_is_ambiguous_extension(file_name_hint, ambiguous_exts, expected):
    result = is_ambiguous_extension(
        file_name_hint,
        ambiguous_extensions=ambiguous_exts,
    )
    assert result == expected


def test_default_settings():
    """Test that default settings are used when no extensions provided"""
    # .ts is in default settings
    assert is_ambiguous_extension("app.ts") is True
    assert is_ambiguous_extension("App.TS") is True
    
    # .js is not in default settings
    assert is_ambiguous_extension("app.js") is False


def test_empty_ambiguous_extensions():
    """Test that empty ambiguous_extensions still uses default settings"""
    # Empty set is merged with defaults, so .ts should still be detected
    assert (
        is_ambiguous_extension("app.ts", ambiguous_extensions=set())
        is True
    )
    # .js is not in defaults
    assert (
        is_ambiguous_extension("app.js", ambiguous_extensions=set())
        is False
    )


def test_pathlike_object():
    """Test that PathLike objects are handled correctly"""
    from pathlib import Path

    path = Path("app.ts")
    result = is_ambiguous_extension(
        path,
        ambiguous_extensions={".ts"},
    )
    assert result is True
