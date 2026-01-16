import os

import pytest

from kiarina.currency.currency_error import ExchangeRateNotFoundError
from kiarina.currency.rate_provider_impl.frankfurter import FrankfurterRateProvider


# Skip real API calls unless explicitly enabled
skip_unless_enabled = pytest.mark.skipif(
    not bool(os.getenv("KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_TEST_ENABLED")),
    reason="Skip real API calls unless KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_TEST_ENABLED is set",
)


@pytest.fixture
def frankfurter_provider():
    """Create a FrankfurterRateProvider"""
    return FrankfurterRateProvider()


@skip_unless_enabled
async def test_same_currency(frankfurter_provider):
    """Test rate for same currency returns 1.0"""
    rate = await frankfurter_provider.get_rate("USD", "USD")
    assert rate == 1.0


@skip_unless_enabled
async def test_get_rate_usd_to_jpy(frankfurter_provider):
    """Test getting USD to JPY exchange rate"""
    rate = await frankfurter_provider.get_rate("USD", "JPY")
    assert isinstance(rate, float)
    assert rate > 0


@skip_unless_enabled
async def test_get_rate_eur_to_usd(frankfurter_provider):
    """Test getting EUR to USD exchange rate"""
    rate = await frankfurter_provider.get_rate("EUR", "USD")
    assert isinstance(rate, float)
    assert rate > 0


@skip_unless_enabled
async def test_get_rate_with_default(frankfurter_provider):
    """Test getting rate with default value for unsupported currency"""
    # Use an invalid currency code
    rate = await frankfurter_provider.get_rate("USD", "XXX", default=1.5)
    assert rate == 1.5


@skip_unless_enabled
async def test_get_rate_unsupported_currency_raises_error(frankfurter_provider):
    """Test that unsupported currency raises ExchangeRateNotFoundError"""
    with pytest.raises(ExchangeRateNotFoundError):
        await frankfurter_provider.get_rate("USD", "XXX")


@skip_unless_enabled
async def test_get_rate_inverted(frankfurter_provider):
    """Test that inverted rates are consistent"""
    # Get USD -> EUR
    usd_to_eur = await frankfurter_provider.get_rate("USD", "EUR")
    # Get EUR -> USD
    eur_to_usd = await frankfurter_provider.get_rate("EUR", "USD")

    # They should be inverses (with some tolerance for API precision)
    assert abs(usd_to_eur * eur_to_usd - 1.0) < 0.01
