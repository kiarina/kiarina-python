from kiarina.currency.rate import get_exchange_rate


async def test_get_exchange_rate() -> None:
    rate = await get_exchange_rate("USD", "EUR")
    assert isinstance(rate, float)
