from unittest.mock import patch

import pytest

from kiarina.utils.mime._operations.detect_with_mimetypes import detect_with_mimetypes


# fmt: off
@pytest.mark.parametrize(
    "mock_guess_type_return,expected",
    [
        # Test case: mimetypes returns a MIME type
        (("text/plain", None), "text/plain"),
        (("application/json", None), "application/json"),
        (("image/png", "gzip"), "image/png"),  # encoding is ignored
        
        # Test case: mimetypes returns None (unknown extension)
        ((None, None), None),
        ((None, "gzip"), None),  # encoding without MIME type
    ],
)
# fmt: on
def test_detect_with_mimetypes(mock_guess_type_return, expected):
    """
    Test detect_with_mimetypes function behavior.
    
    This test focuses on how the function processes the return value from
    mimetypes.guess_type(), rather than testing the mimetypes module itself.
    """
    with patch('kiarina.utils.mime._operations.detect_with_mimetypes.guess_type') as mock_guess_type:
        mock_guess_type.return_value = mock_guess_type_return
        
        result = detect_with_mimetypes("any_filename.ext")
        assert result == expected
        
        # Verify that guess_type was called with correct parameters
        mock_guess_type.assert_called_once_with("any_filename.ext", strict=False)


def test_detect_with_mimetypes_integration():
    """
    Integration test that verifies the function works with the actual mimetypes module.
    
    This test ensures the function doesn't crash and handles real mimetypes results properly.
    """
    # Test with a filename that should be recognized by most systems
    result = detect_with_mimetypes("test.txt")
    
    # We don't assert specific values due to environment differences,
    # but we ensure the result is either None or a valid MIME type string
    assert result is None or (isinstance(result, str) and "/" in result)
    
    # Test with unknown extension
    result_unknown = detect_with_mimetypes("unknown.unknownext")
    assert result_unknown is None
