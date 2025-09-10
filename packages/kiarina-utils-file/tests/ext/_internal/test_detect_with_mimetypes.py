from unittest.mock import patch

import pytest

from kiarina.utils.ext._operations.detect_with_mimetypes import detect_with_mimetypes


# fmt: off
@pytest.mark.parametrize(
    "mime_type,mock_guess_extension_return,expected",
    [
        # Test case: mimetypes returns an extension
        ("text/plain", ".txt", ".txt"),
        ("application/json", ".json", ".json"),
        ("image/png", ".png", ".png"),
        
        # Test case: mimetypes returns None (unknown MIME type)
        ("application/unknown", None, None),
        ("text/nonexistent", None, None),
        
        # Test case: MIME type with parameters (should be normalized)
        ("text/html; charset=utf-8", ".html", ".html"),
        
        # Test case: empty MIME type
        ("", None, None),
    ],
)
# fmt: on
def test_detect_with_mimetypes(mime_type, mock_guess_extension_return, expected):
    """
    Test detect_with_mimetypes function behavior.
    
    This test focuses on how the function processes the return value from
    mimetypes.guess_extension(), rather than testing the mimetypes module itself.
    """
    with patch('kiarina.utils.ext._operations.detect_with_mimetypes.guess_extension') as mock_guess_extension:
        mock_guess_extension.return_value = mock_guess_extension_return
        
        result = detect_with_mimetypes(mime_type)
        assert result == expected
        
        # Verify that guess_extension was called with correct parameters
        # The function should normalize the MIME type (remove parameters)
        expected_normalized = mime_type.split(";")[0].strip().lower() if mime_type else ""
        mock_guess_extension.assert_called_once_with(expected_normalized, strict=False)


def test_detect_with_mimetypes_integration():
    """
    Integration test that verifies the function works with the actual mimetypes module.
    
    This test ensures the function doesn't crash and handles real mimetypes results properly.
    """
    # Test with a MIME type that should be recognized by most systems
    result = detect_with_mimetypes("text/plain")
    
    # We don't assert specific values due to environment differences,
    # but we ensure the result is either None or a valid extension string
    assert result is None or (isinstance(result, str) and result.startswith("."))
    
    # Test with unknown MIME type
    result_unknown = detect_with_mimetypes("application/unknown-mime-type")
    assert result_unknown is None
