from kiarina.currency.currency_code import CurrencyCode
from kiarina.currency.currency_error import ExchangeRateNotFoundError
from kiarina.currency.rate_provider import BaseRateProvider

from .._settings import settings_manager


class StaticRateProvider(BaseRateProvider):
    async def get_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        *,
        default: float | None = None,
    ) -> float:
        settings = settings_manager.get_settings()

        if from_currency == to_currency:
            return 1.0

        if from_currency in settings.rates:
            if to_currency in settings.rates[from_currency]:
                return settings.rates[from_currency][to_currency]

        if to_currency in settings.rates:
            if from_currency in settings.rates[to_currency]:
                return 1.0 / settings.rates[to_currency][from_currency]

        base = settings.base_currency
        if base != from_currency and base != to_currency:
            from_to_base = None
            base_to_to = None

            if (
                from_currency in settings.rates
                and base in settings.rates[from_currency]
            ):
                from_to_base = settings.rates[from_currency][base]
            elif base in settings.rates and from_currency in settings.rates[base]:
                from_to_base = 1.0 / settings.rates[base][from_currency]

            if base in settings.rates and to_currency in settings.rates[base]:
                base_to_to = settings.rates[base][to_currency]
            elif to_currency in settings.rates and base in settings.rates[to_currency]:
                base_to_to = 1.0 / settings.rates[to_currency][base]

            if from_to_base is not None and base_to_to is not None:
                return from_to_base * base_to_to

        if default is None:
            raise ExchangeRateNotFoundError(
                f"Exchange rate not found from {from_currency} to {to_currency}"
            )

        return default
