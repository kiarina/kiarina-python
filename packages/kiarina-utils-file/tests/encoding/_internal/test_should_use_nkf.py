import os
from unittest.mock import patch

from kiarina.utils.encoding._operations.should_use_nkf import (
    clear_nkf_cache,
    should_use_nkf,
)


@patch("kiarina.utils.encoding._operations.should_use_nkf.shutil.which")
@patch("kiarina.utils.encoding._operations.should_use_nkf.locale.getlocale")
def test_jp(mock_getlocale, mock_which):
    """Test that should_use_nkf returns True when nkf is available in Japanese environment"""
    clear_nkf_cache()
    mock_getlocale.return_value = ("ja_JP", "UTF-8")
    mock_which.return_value = "/usr/bin/nkf"

    assert should_use_nkf() is True
    mock_getlocale.assert_called_once()
    mock_which.assert_called_once_with("nkf")


@patch.dict(
    os.environ, {"LANG": "en_US.UTF-8", "LC_ALL": "", "LC_CTYPE": ""}, clear=False
)
@patch("kiarina.utils.encoding._operations.should_use_nkf.shutil.which")
@patch("kiarina.utils.encoding._operations.should_use_nkf.locale.getlocale")
def test_non_jp(mock_getlocale, mock_which):
    """Test that should_use_nkf returns False when nkf is available in non-Japanese environment"""
    clear_nkf_cache()
    mock_getlocale.return_value = ("en_US", "UTF-8")
    mock_which.return_value = "/usr/bin/nkf"

    assert should_use_nkf() is False
    mock_getlocale.assert_called_once()
    mock_which.assert_called_once_with("nkf")
