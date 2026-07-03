from kiarina.currency import CurrencyCode


def format_cost(
    microdollars: int,
    *,
    currency: CurrencyCode | None = None,
    exchange_rate: float | None = None,
    decimal_places: int | None = None,
) -> str:
    if currency and exchange_rate and currency != "USD":
        amount = (microdollars / 1_000_000) * exchange_rate
    else:
        amount = microdollars / 1_000_000
        currency = "USD"

    if decimal_places is None:
        format_string = "{:f} {}"
    else:
        format_string = f"{{:.{decimal_places}f}} {{}}"

    return format_string.format(amount, currency)
