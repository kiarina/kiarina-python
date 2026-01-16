from unittest.mock import patch

from kiarina.currency.system_currency import get_system_currency


def test_get_system_currency_returns_valid_code():
    """Test that get_system_currency returns a valid currency code"""
    currency = get_system_currency()
    assert isinstance(currency, str)
    assert len(currency) == 3
    assert currency.isupper()


def test_get_system_currency_with_int_curr_symbol():
    """Test currency detection from int_curr_symbol"""
    mock_conv = {"int_curr_symbol": "JPY "}

    with patch("locale.localeconv", return_value=mock_conv):
        currency = get_system_currency()
        assert currency == "JPY"


def test_get_system_currency_with_locale_ja():
    """Test currency detection from Japanese locale"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=("ja_JP", "UTF-8")),
    ):
        currency = get_system_currency()
        assert currency == "JPY"


def test_get_system_currency_with_locale_en_us():
    """Test currency detection from US locale"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=("en_US", "UTF-8")),
    ):
        currency = get_system_currency()
        assert currency == "USD"


def test_get_system_currency_with_locale_en_gb():
    """Test currency detection from UK locale"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=("en_GB", "UTF-8")),
    ):
        currency = get_system_currency()
        assert currency == "GBP"


def test_get_system_currency_with_locale_de():
    """Test currency detection from German locale"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=("de_DE", "UTF-8")),
    ):
        currency = get_system_currency()
        assert currency == "EUR"


def test_get_system_currency_with_locale_zh_cn():
    """Test currency detection from Chinese locale"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=("zh_CN", "UTF-8")),
    ):
        currency = get_system_currency()
        assert currency == "CNY"


def test_get_system_currency_with_env_var():
    """Test currency detection from environment variable"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=(None, None)),
        patch.dict("os.environ", {"LANG": "en_US.UTF-8"}),
    ):
        currency = get_system_currency()
        assert currency == "USD"


def test_get_system_currency_fallback_to_usd():
    """Test fallback to USD when locale detection fails"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=(None, None)),
        patch.dict("os.environ", {}, clear=True),
    ):
        currency = get_system_currency()
        assert currency == "USD"


def test_get_system_currency_with_exception():
    """Test fallback to USD when exception occurs"""
    with patch("locale.localeconv", side_effect=Exception("Test error")):
        currency = get_system_currency()
        assert currency == "USD"


def test_get_system_currency_with_invalid_int_curr_symbol():
    """Test fallback when int_curr_symbol is invalid"""
    mock_conv = {"int_curr_symbol": ""}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=("en_US", "UTF-8")),
    ):
        currency = get_system_currency()
        assert currency == "USD"


def test_get_system_currency_with_getlocale_exception():
    """Test fallback when getlocale raises exception"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", side_effect=Exception("Test error")),
        patch.dict("os.environ", {"LANG": "en_US.UTF-8"}),
    ):
        currency = get_system_currency()
        assert currency == "USD"


def test_get_system_currency_with_env_var_exception():
    """Test fallback when environment variable parsing raises exception"""
    mock_conv = {}

    with (
        patch("locale.localeconv", return_value=mock_conv),
        patch("locale.getlocale", return_value=(None, None)),
        patch.dict("os.environ", {"LANG": "en_US.UTF-8"}),
        patch("os.environ.__getitem__", side_effect=Exception("Test error")),
    ):
        currency = get_system_currency()
        assert currency == "USD"
