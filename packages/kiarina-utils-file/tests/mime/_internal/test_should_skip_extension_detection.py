import pytest

from kiarina.utils.mime._operations.should_skip_extension_detection import (
    should_skip_extension_detection,
)


# fmt: off
@pytest.mark.parametrize(
    "file_name_hint,skip_suffixes,expected",
    [
        # Basic matching
        ("app.ts", {".ts"}, True),
        ("app.js", {".ts"}, False),
        ("app.ts", set(), True),  # Empty set merges with defaults (.ts is in defaults)
        
        # Case insensitive matching
        ("App.TS", {".ts"}, True),
        ("APP.TS", {".ts"}, True),
        ("app.ts", {".TS"}, True),
        
        # Multiple suffixes
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
def test_should_skip_extension_detection(file_name_hint, skip_suffixes, expected):
    result = should_skip_extension_detection(
        file_name_hint,
        skip_extension_detection_suffixes=skip_suffixes,
    )
    assert result == expected


def test_default_settings():
    """Test that default settings are used when no suffixes provided"""
    # .ts is in default settings
    assert should_skip_extension_detection("app.ts") is True
    assert should_skip_extension_detection("App.TS") is True
    
    # .js is not in default settings
    assert should_skip_extension_detection("app.js") is False


def test_empty_skip_suffixes():
    """Test that empty skip_suffixes still uses default settings"""
    # Empty set is merged with defaults, so .ts should still be detected
    assert (
        should_skip_extension_detection("app.ts", skip_extension_detection_suffixes=set())
        is True
    )
    # .js is not in defaults
    assert (
        should_skip_extension_detection("app.js", skip_extension_detection_suffixes=set())
        is False
    )


def test_pathlike_object():
    """Test that PathLike objects are handled correctly"""
    from pathlib import Path

    path = Path("app.ts")
    result = should_skip_extension_detection(
        path,
        skip_extension_detection_suffixes={".ts"},
    )
    assert result is True
